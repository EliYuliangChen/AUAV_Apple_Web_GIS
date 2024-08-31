from flask import Flask, send_file, jsonify, send_from_directory
import sqlite3
import io

app = Flask(__name__)

@app.route('/detail_image/<path:filename>')
def detail_image(filename):
    return send_from_directory('detail_image', filename)

def get_tile(z, x, y, db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    
    cur.execute("SELECT EXISTS(SELECT 1 FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?)", (z, x, 2**z-1-y))
    exists = cur.fetchone()[0]
    
    if exists:
        cur.execute("SELECT tile_data FROM tiles WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?", (z, x, 2**z-1-y))
        tile_data = cur.fetchone()[0]
        return send_file(io.BytesIO(tile_data), mimetype='image/png')
    else:
        return '', 204

@app.route('/tiles/<int:z>/<int:x>/<int:y>.png')
def serve_tile(z, x, y):
    if z == 22:
        return get_tile(z, x, y, 'high_res.mbtiles')
    else:
        return get_tile(z, x, y, 'low_res_output.mbtiles')

@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/output.geojson')
def serve_geojson():
    return send_file('output.geojson', mimetype='application/json')

@app.route('/metadata')
def get_metadata():
    conn = sqlite3.connect('low_res_output.mbtiles')
    cur = conn.cursor()
    cur.execute("SELECT name, value FROM metadata")
    metadata = dict(cur.fetchall())
    return jsonify(metadata)

if __name__ == '__main__':
    app.run(debug=True)
