"""Shared browser toolkit for the individual DAA project."""
import html
import json
import os
import secrets
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs


def esc(value):
    return html.escape(str(value), quote=True)


def heading(text):
    return '<h2>' + esc(text) + '</h2>'


def note(text):
    return '<p class="note">' + esc(text) + '</p>'


def table(headers, rows):
    cells = ''.join('<th>' + esc(x) + '</th>' for x in headers)
    body = ''.join('<tr>' + ''.join('<td>' + esc(x) + '</td>' for x in row) + '</tr>' for row in rows)
    if not body:
        body = '<tr><td colspan="' + str(len(headers)) + '">No records</td></tr>'
    return '<div class="scroll"><table><thead><tr>' + cells + '</tr></thead><tbody>' + body + '</tbody></table></div>'


def form(action, fields, button):
    out = '<form method="post"><input type="hidden" name="_csrf" value="{TOKEN}">'
    out += '<input type="hidden" name="action" value="' + esc(action) + '">'
    for name, label, kind, value in fields:
        out += '<label>' + esc(label)
        if kind in ('textarea', 'textarea_optional'):
            required = ' required' if kind == 'textarea' else ''
            out += '<textarea name="' + esc(name) + '"' + required + '>' + esc(value) + '</textarea>'
        elif kind == 'select':
            out += '<select name="' + esc(name) + '">'
            for option in value:
                out += '<option value="' + esc(option) + '">' + esc(option) + '</option>'
            out += '</select>'
        else:
            out += '<input type="' + esc(kind) + '" name="' + esc(name) + '" value="' + esc(value) + '">'
        out += '</label>'
    return out + '<button type="submit">' + esc(button) + '</button></form>'


class Store:
    def __init__(self, path, default):
        self.path = Path(path)
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding='utf-8'))
            except (json.JSONDecodeError, OSError):
                self.data = default
        else:
            self.data = default

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.data, indent=2), encoding='utf-8')
        temp.replace(self.path)


def run(title, view, handle):
    token = secrets.token_urlsafe(24)
    port = int(os.environ.get('PORT', '8000'))

    class Handler(BaseHTTPRequestHandler):
        def send_page(self, extra=''):
            body = '<!doctype html><html lang="en"><head><meta charset="utf-8">'
            body += '<meta name="viewport" content="width=device-width,initial-scale=1">'
            body += '<title>' + esc(title) + '</title><style>'
            body += """
            :root{color-scheme:light}*{box-sizing:border-box}
            body{font:15px/1.55 system-ui,-apple-system,sans-serif;background:#f3f6fb;margin:0;color:#172033}
            main{max-width:1120px;margin:32px auto;padding:28px;background:#fff;border:1px solid #e2e8f0;border-radius:16px;box-shadow:0 12px 34px #0f172a0a}
            h1{font-size:clamp(25px,4vw,36px);line-height:1.15;margin:0 0 8px;letter-spacing:-.7px}
            h2{font-size:20px;margin:28px 0 12px}p{color:#475569}.eyebrow{font-size:12px;text-transform:uppercase;letter-spacing:1.5px;color:#2563eb;font-weight:700}
            form{padding:18px;border:1px solid #e2e8f0;border-radius:12px;margin:14px 0;background:#fbfdff}
            label{display:block;font-weight:600;margin:10px 0;color:#334155}
            input,select,textarea{display:block;width:100%;padding:11px 12px;margin-top:6px;font:inherit;border:1px solid #cbd5e1;border-radius:8px;background:white;color:#0f172a}
            button{background:#1d4ed8;color:white;border:0;padding:11px 17px;border-radius:8px;font:inherit;font-weight:650;cursor:pointer;margin-top:8px}
            button:hover{background:#1e40af}.scroll{overflow:auto;border:1px solid #e2e8f0;border-radius:10px}
            table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #e2e8f0;padding:10px 12px;text-align:left;overflow-wrap:anywhere}
            th{background:#f8fafc;color:#334155;font-weight:700}tr:last-child td{border-bottom:0}.note{padding:12px 14px;border-radius:9px;background:#eff6ff;color:#1e40af}
            .sub{color:#64748b;margin:0 0 22px}.pill{display:inline-block;background:#eff6ff;color:#1d4ed8;border-radius:999px;padding:4px 9px;font-size:12px;font-weight:700}
            .footer{margin-top:28px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:12px;color:#64748b}
            """
            body += '</style></head><body><main><div class="eyebrow">DAA • Individual project</div>'
            body += '<h1>' + esc(title) + '</h1>'
            body += '<p class="sub">Duplicate detection, safe organization, and reversible file operations.</p>'
            body += extra + view()
            body += '<div class="footer">Local learning prototype • Originals are not deleted • Use a practice folder first</div>'
            body += '</main></body></html>'
            body = body.replace('{TOKEN}', token).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path != '/':
                self.send_error(404)
                return
            self.send_page()

        def do_POST(self):
            try:
                if self.path != '/':
                    raise ValueError('Unknown page.')
                length = int(self.headers.get('Content-Length', '0'))
                if length < 1 or length > 1_000_000:
                    raise ValueError('Request is empty or too large.')
                raw = self.rfile.read(length).decode('utf-8')
                data = {k: v[0] for k, v in parse_qs(raw, keep_blank_values=True).items()}
                if not secrets.compare_digest(data.get('_csrf', ''), token):
                    raise ValueError('Refresh the page and try again.')
                self.send_page(handle(data) or note('Action completed.'))
            except (ValueError, KeyError, OSError) as error:
                self.send_page(note('Please check: ' + str(error)))

        def log_message(self, *args):
            pass

    server = HTTPServer(('127.0.0.1', port), Handler)
    print(f'{title}: open http://127.0.0.1:{port}')
    print('Keep this terminal open. Press Ctrl+C to stop.')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
