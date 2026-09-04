import csv, io
from flask import Response

def export_csv(data, headers, filename='export.csv'):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row)
    response = Response(output.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition': f'attachment; filename={filename}'})
    return response
