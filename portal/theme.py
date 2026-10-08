from django.utils.deprecation import MiddlewareMixin


class ThemeMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if "text/html" not in response.get("Content-Type", "") or not hasattr(response, "content"):
            return response
        widget = '''<button id="automation-theme-toggle" type="button">◐ Theme</button><style>
        #automation-theme-toggle{position:fixed;right:18px;bottom:18px;z-index:99999;border:0;border-radius:999px;padding:10px 15px;background:#172033;color:#fff;box-shadow:0 5px 18px #0003;cursor:pointer;font:600 13px system-ui}
        html.automation-dark body{background:#101522!important;color:#f1f5f9!important}
        html.automation-dark .card,html.automation-dark section,html.automation-dark article,html.automation-dark table,html.automation-dark .notice{background:#1b2435!important;color:#f1f5f9!important;border-color:#3b4a63!important}
        html.automation-dark h1,html.automation-dark h2,html.automation-dark h3,html.automation-dark h4,html.automation-dark p,html.automation-dark label,html.automation-dark span,html.automation-dark li,html.automation-dark td,html.automation-dark th,html.automation-dark legend,html.automation-dark strong,html.automation-dark b{color:#f1f5f9!important}html.automation-dark .module-list label,html.automation-dark .module-list label span{color:#f1f5f9!important}
        html.automation-dark .muted,html.automation-dark .hint,html.automation-dark small{color:#b8c4d6!important}
        html.automation-dark input,html.automation-dark textarea,html.automation-dark select{background:#111827!important;color:#f1f5f9!important;border-color:#52637e!important}
        html.automation-dark input::placeholder,html.automation-dark textarea::placeholder{color:#9aa9bf!important}
        html.automation-dark a{color:#a9c0ff!important}html.automation-dark button,html.automation-dark .btn{color:#fff!important}html.automation-dark #automation-theme-toggle{background:#f4c95d!important;color:#172033!important}
        </style><script>(function(){var k="automation-theme",h=document.documentElement;if(localStorage.getItem(k)==="dark")h.classList.add("automation-dark");var b=document.getElementById("automation-theme-toggle");if(b)b.onclick=function(){h.classList.toggle("automation-dark");localStorage.setItem(k,h.classList.contains("automation-dark")?"dark":"light")}})();</script>'''
        body = response.content.decode(response.charset or "utf-8")
        if "automation-theme-toggle" not in body and "</body>" in body:
            body = body.replace("</body>", widget + "</body>")
            response.content = body.encode(response.charset or "utf-8")
            response["Content-Length"] = str(len(response.content))
        return response
