from django.utils.deprecation import MiddlewareMixin


class ThemeMiddleware(MiddlewareMixin):
    """Add the shared responsive app shell and persistent light/dark theme."""

    STYLE_SCRIPT = """
    <style>
      :root{color-scheme:light;--page:#f4f7fc;--surface:#fff;--surface-soft:#f8faff;--text:#17233b;--muted:#687791;--border:#e0e7f1;--accent:#2463eb;--shadow:0 8px 24px #17233b0c}
      html.automation-dark{color-scheme:dark;--page:#111a27;--surface:#1a2636;--surface-soft:#223146;--text:#eff4fb;--muted:#aab8ca;--border:#34465d;--accent:#6794ff;--shadow:0 10px 28px #0003}
      body{margin:0!important;padding-left:248px!important;min-height:100vh;background:radial-gradient(ellipse at 84% 0%,#3975df0d,transparent 35%),var(--page)!important;color:var(--text);font-family:Inter,"Segoe UI",system-ui,-apple-system,sans-serif!important;box-sizing:border-box}
      body *{box-sizing:border-box}
      #ambient-particles{position:fixed;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;opacity:.88}
      html.automation-dark #ambient-particles{opacity:.58}
      body>main,body>.container,body>.shell,body>.wrap{position:relative;z-index:1}
      .app-sidebar{position:fixed;z-index:10000;inset:0 auto 0 0;width:248px;padding:22px 16px 16px;background:linear-gradient(180deg,#111d30,#0d1727);color:#e8eef9;display:flex;flex-direction:column;box-shadow:8px 0 30px #0e1b2b16;animation:sidebar-enter .35s ease-out both}
      .app-brand{display:flex;align-items:center;gap:11px;padding:2px 8px 26px;color:#fff;font-weight:750;font-size:16px;letter-spacing:-.2px}
      .app-brand-mark{width:32px;height:32px;border-radius:10px;background:linear-gradient(145deg,#4386ff,#2455d9);display:grid;place-items:center;color:#fff;font-weight:800;box-shadow:0 5px 14px #2463eb55}
      .app-nav{display:grid;gap:6px}
      .app-nav a{display:flex;align-items:center;gap:12px;min-height:42px;padding:0 11px;border-radius:9px;color:#c4cfdf;text-decoration:none;font-size:13px;font-weight:550;transition:background .18s,color .18s,transform .18s,box-shadow .18s}
      .app-nav a:hover{background:#ffffff12;color:#fff}
      .app-nav a.is-active{background:linear-gradient(100deg,#2867df,#1d55bc);color:#fff;box-shadow:0 5px 16px #1c59c84a}
      .app-nav-icon{width:19px;text-align:center;color:#d6e2f4;font-size:15px}
      .app-subnav{display:grid;gap:2px;margin:2px 0 5px 31px;padding-left:10px;border-left:1px solid #ffffff28}
      .app-subnav a{min-height:31px;padding:0 8px;font-size:11px;color:#aebbd0}
      .app-subnav a.is-current{color:#fff;background:#ffffff12;border-radius:7px}
      .app-sidebar-spacer{flex:1}
      .app-profile{display:flex;align-items:center;gap:10px;border-top:1px solid #ffffff1e;padding:17px 5px 14px;color:#fff;font-size:12px}
      .app-avatar{width:32px;height:32px;display:grid;place-items:center;border-radius:50%;background:#3474e8;color:#fff;font-weight:700}
      .app-profile small{display:block;margin-top:3px;color:#9eacc0;font-size:10px}
      .app-sidebar-bottom{display:grid;gap:5px}
      .app-sidebar-bottom button,.app-sidebar-bottom a{display:flex;align-items:center;gap:10px;min-height:38px;padding:0 9px;border:0;border-radius:8px;background:transparent;color:#d6e0ef;text-decoration:none;font:550 12px system-ui;cursor:pointer}
      .app-sidebar-bottom button:hover,.app-sidebar-bottom a:hover{background:#ffffff12;color:#fff}
      #mobile-menu-toggle{display:none;position:fixed;z-index:10002;top:13px;left:13px;width:44px;height:42px;padding:10px;border:1px solid #dce4ef;border-radius:11px;background:#fff;box-shadow:0 4px 14px #17233b18;cursor:pointer}
      #mobile-menu-toggle span{display:block;width:20px;height:2px;margin:4px auto;border-radius:2px;background:#182b48;transition:transform .18s,opacity .18s}
      #mobile-menu-toggle[aria-expanded="true"] span:nth-child(1){transform:translateY(6px) rotate(45deg)}
      #mobile-menu-toggle[aria-expanded="true"] span:nth-child(2){opacity:0}
      #mobile-menu-toggle[aria-expanded="true"] span:nth-child(3){transform:translateY(-6px) rotate(-45deg)}
      #app-menu-backdrop{display:none}
      body.app-menu-open{overflow:hidden}
      body{color:var(--text)}
      .nav{display:none!important}
      h1,h2,h3,h4{color:var(--text);letter-spacing:-.025em}
      .card,article,.search-box,.summary-card,.table-box,.progress-box,.status-wrap{border-color:var(--border)!important;border-radius:15px!important;box-shadow:var(--shadow);animation:content-enter .38s cubic-bezier(.2,.7,.2,1) both;transition:transform .2s ease,box-shadow .2s ease,border-color .2s ease}
      @keyframes sidebar-enter{from{opacity:0}to{opacity:1}}
      @keyframes content-enter{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
      .card:hover,article:hover,.search-box:hover,.summary-card:hover{transform:translateY(-2px);box-shadow:0 14px 32px #17233b14}
      main>*:nth-child(2){animation-delay:.035s}main>*:nth-child(3){animation-delay:.07s}main>*:nth-child(4){animation-delay:.105s}
      .app-nav a:hover{transform:translateX(2px)}
      button,.btn{transition:transform .15s ease,background .15s ease,box-shadow .15s ease}
      button:hover,.btn:hover{transform:translateY(-1px)}
      a:not(.app-nav-link):not(.app-subnav a):not(.app-sidebar-bottom a){transition:color .15s ease,background-color .15s ease,box-shadow .15s ease}
      a:focus-visible,button:focus-visible{outline:3px solid #5d8cff85!important;outline-offset:2px}
      button:not(.app-menu-button):not(#automation-theme-toggle):hover,.btn:hover{filter:brightness(1.06);box-shadow:0 5px 14px #174ba52b}
      input:not([type=checkbox]):not([type=radio]),textarea,select{transition:border-color .15s,box-shadow .15s,background-color .15s}
      input:focus,textarea:focus,select:focus{outline:3px solid #2463eb30;border-color:#2463eb!important}
      .table-wrapper,.table-wrap{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;overscroll-behavior-x:contain}
      tbody tr{transition:background-color .15s ease,color .15s ease}
      tbody tr:hover td{background:#f1f6ff!important;color:#17233b!important}
      tbody tr:hover td a{color:#174cae!important;text-decoration:underline;text-underline-offset:2px}
      html.automation-dark body{background:var(--page)!important;color:var(--text)!important}
      html.automation-dark .card,html.automation-dark article,html.automation-dark section,html.automation-dark .search-box,html.automation-dark .table-box,html.automation-dark .summary-card,html.automation-dark .status-wrap,html.automation-dark .notice,html.automation-dark .tag-box,html.automation-dark .progress-box{background:var(--surface)!important;color:var(--text)!important;border-color:var(--border)!important;box-shadow:var(--shadow)}
      html.automation-dark h1,html.automation-dark h2,html.automation-dark h3,html.automation-dark h4,html.automation-dark p,html.automation-dark label,html.automation-dark span,html.automation-dark li,html.automation-dark td,html.automation-dark th,html.automation-dark legend,html.automation-dark strong,html.automation-dark b{color:var(--text)}
      html.automation-dark .muted,html.automation-dark .hint,html.automation-dark small,html.automation-dark .subtitle,html.automation-dark .filter-info,html.automation-dark .table-subtitle{color:var(--muted)!important}
      html.automation-dark input:not([type=checkbox]):not([type=radio]):not([type=submit]),html.automation-dark textarea,html.automation-dark select{background:#121d2b!important;color:#f4f7fc!important;border:1px solid #52647c!important;caret-color:#fff}
      html.automation-dark input::placeholder,html.automation-dark textarea::placeholder{color:#a7b4c6!important;opacity:1}
      html.automation-dark input:focus,html.automation-dark textarea:focus,html.automation-dark select:focus{background:#121d2b!important;color:#fff!important;border-color:#8eabff!important;outline:3px solid #7898ff45;box-shadow:0 0 0 2px #7898ff22}
      html.automation-dark option{background:#121d2b;color:#f4f7fc}
      html.automation-dark table{background:var(--surface)!important;color:var(--text)}
      html.automation-dark th,html.automation-dark td{border-color:var(--border)!important}
      html.automation-dark table th,html.automation-dark table thead th{background:#26374d!important;color:#edf4ff!important}
      html.automation-dark tbody tr:hover td,html.automation-dark .lead-row:hover td{background:#263b56!important;color:#f4f7fc!important}
      html.automation-dark tbody tr:hover td a,html.automation-dark .lead-row:hover td a{color:#c3d7ff!important;text-decoration:underline;text-underline-offset:2px}
      html.automation-dark .lead-row:hover .website-no,html.automation-dark .lead-row:hover .no-social{color:#ffb7b7!important}
      html.automation-dark .lead-row:hover .website-yes{color:#9af0c3!important}
      html.automation-dark a:hover:not(.app-nav-link):not(.app-subnav a):not(.app-sidebar-bottom a){color:#fff!important;background:#ffffff12;border-radius:4px}
      html.automation-dark .app-nav a:hover,html.automation-dark .app-subnav a:hover,html.automation-dark .app-sidebar-bottom a:hover{color:#fff!important;background:#ffffff12}
      html.automation-dark a:not(.btn):not(.app-nav-link){color:#a9c0ff}
      html.automation-dark button:not(.app-menu-button),html.automation-dark .btn{color:#fff}
      html.automation-dark .filter-label{color:var(--text)!important}
      html.automation-dark .filter-label:hover,html.automation-dark .progress-track{background:var(--surface-soft)!important}
      html.automation-dark #mobile-menu-toggle{background:#1d2b3e;border-color:#465a73}
      html.automation-dark #mobile-menu-toggle span{background:#f4f7fc}
      .standalone-theme-toggle{position:fixed;z-index:10000;right:18px;bottom:18px;padding:11px 16px;border:1px solid #dce4ef;border-radius:999px;background:#172a48;color:#fff;font:600 13px system-ui;box-shadow:0 5px 18px #07142635;cursor:pointer}
      html.automation-dark .standalone-theme-toggle{background:#26364b;color:#fff;border-color:#50627a}
      @media(max-width:900px){body{padding-left:0!important}.app-sidebar{width:270px;transform:translateX(-105%);transition:transform .22s ease;box-shadow:12px 0 32px #07142645}.app-sidebar.is-open{transform:translateX(0)}#mobile-menu-toggle{display:block}#app-menu-backdrop.is-visible{display:block;position:fixed;z-index:9998;inset:0;background:#08142678;backdrop-filter:blur(2px)}body:has(#mobile-menu-toggle) main,body:has(#mobile-menu-toggle) .container{padding-top:68px!important}.nav{display:none!important}}
      @media(max-width:640px){.container{width:100%!important;margin:0 auto!important;padding:68px 14px 28px!important}.shell{width:100%;padding:68px 14px 28px!important}.wrap{width:100%;padding:68px 14px 28px!important}.grid,.form-grid,.summary,.stat-grid,.status-grid{grid-template-columns:1fr!important}.full{grid-column:auto!important}.hero{display:block!important}.hero h1{font-size:26px!important}.card{padding:17px!important}.search-row{align-items:stretch!important}.search-row input[type=text],.search-row input[type=number]{width:100%!important;min-width:0!important}.search-row button{flex:1 1 42%;min-width:0}.filters{display:grid!important;gap:9px}.status-grid{display:grid!important}.table-wrapper table,.table-wrap table{min-width:680px}.actions{flex-wrap:wrap}.actions button,.actions .btn{width:100%}.tool-back{left:12px;top:12px}}
      @media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
    </style>
    <script>
      (function(){
        var root=document.documentElement,key="automation-theme";
        try{if(localStorage.getItem(key)==="dark")root.classList.add("automation-dark")}catch(e){}
        document.addEventListener("DOMContentLoaded",function(){
          var toggle=document.getElementById("automation-theme-toggle"),menu=document.getElementById("mobile-menu-toggle"),side=document.querySelector(".app-sidebar"),backdrop=document.getElementById("app-menu-backdrop");
          if(toggle)toggle.addEventListener("click",function(){root.classList.toggle("automation-dark");try{localStorage.setItem(key,root.classList.contains("automation-dark")?"dark":"light")}catch(e){}});
          function closeMenu(){if(side)side.classList.remove("is-open");if(backdrop)backdrop.classList.remove("is-visible");if(menu){menu.setAttribute("aria-expanded","false");menu.setAttribute("aria-label","Open navigation menu")}document.body.classList.remove("app-menu-open")}
          function openMenu(){if(side)side.classList.add("is-open");if(backdrop)backdrop.classList.add("is-visible");if(menu){menu.setAttribute("aria-expanded","true");menu.setAttribute("aria-label","Close navigation menu")}document.body.classList.add("app-menu-open")}
          if(menu)menu.addEventListener("click",function(){if(menu.getAttribute("aria-expanded")==="true")closeMenu();else openMenu()});
          if(backdrop)backdrop.addEventListener("click",closeMenu);
          document.addEventListener("keydown",function(e){if(e.key==="Escape")closeMenu()});
          window.addEventListener("resize",function(){if(window.innerWidth>900)closeMenu()});
          if(side)side.querySelectorAll("a").forEach(function(a){a.addEventListener("click",closeMenu)});

          var canvas=document.getElementById("ambient-particles");
          if(!canvas)return;
          var ctx=canvas.getContext("2d");if(!ctx)return;
          var points=[],pointer={x:-1000,y:-1000,active:false},reduced=window.matchMedia("(prefers-reduced-motion: reduce)");
          function resize(){
            var dpr=Math.min(window.devicePixelRatio||1,1.5),w=window.innerWidth,h=window.innerHeight,mobile=w<700;
            canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);canvas.style.width=w+"px";canvas.style.height=h+"px";ctx.setTransform(dpr,0,0,dpr,0,0);
            var count=Math.max(mobile?30:42,Math.min(mobile?56:112,Math.round(w*h/(mobile?9500:12000))));
            points=Array.from({length:count},function(){return{x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.38,vy:(Math.random()-.5)*.38,r:Math.random()*1.45+1.15}});draw(false);
          }
          function draw(move){
            var w=window.innerWidth,h=window.innerHeight,dark=root.classList.contains("automation-dark"),limit=155;
            ctx.clearRect(0,0,w,h);
            for(var i=0;i<points.length;i++){
              var a=points[i];if(move){a.x+=a.vx;a.y+=a.vy;if(a.x<0||a.x>w)a.vx*=-1;if(a.y<0||a.y>h)a.vy*=-1;a.x=Math.max(0,Math.min(w,a.x));a.y=Math.max(0,Math.min(h,a.y))}
              for(var j=i+1;j<points.length;j++){var b=points[j],dx=a.x-b.x,dy=a.y-b.y,dist=Math.sqrt(dx*dx+dy*dy);if(dist<limit){ctx.beginPath();ctx.strokeStyle=dark?"rgba(151,184,255,"+(1-dist/limit)*.28+")":"rgba(31,78,157,"+(1-dist/limit)*.25+")";ctx.lineWidth=dark?1:.95;ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()}}
              if(pointer.active){var px=a.x-pointer.x,py=a.y-pointer.y,pd=Math.sqrt(px*px+py*py);if(pd<190){ctx.beginPath();ctx.strokeStyle=dark?"rgba(174,199,255,"+(1-pd/190)*.55+")":"rgba(24,76,174,"+(1-pd/190)*.5+")";ctx.lineWidth=1.15;ctx.moveTo(a.x,a.y);ctx.lineTo(pointer.x,pointer.y);ctx.stroke()}}
              ctx.beginPath();ctx.fillStyle=dark?"rgba(186,207,255,.78)":"rgba(31,78,157,.7)";ctx.arc(a.x,a.y,a.r,0,Math.PI*2);ctx.fill();
            }
          }
          var frame=0;function animate(){frame=0;if(document.hidden)return;draw(!reduced.matches);if(!reduced.matches)frame=requestAnimationFrame(animate)}
          document.addEventListener("pointermove",function(e){pointer.x=e.clientX;pointer.y=e.clientY;pointer.active=true;if(reduced.matches)draw(false)},{passive:true});
          document.addEventListener("pointerleave",function(){pointer.active=false;if(reduced.matches)draw(false)},{passive:true});
          window.addEventListener("blur",function(){pointer.active=false;if(reduced.matches)draw(false)});
          window.addEventListener("resize",resize,{passive:true});
          document.addEventListener("visibilitychange",function(){if(document.hidden&&frame){cancelAnimationFrame(frame);frame=0}else if(!document.hidden&&!reduced.matches&&!frame){frame=requestAnimationFrame(animate)}});
          resize();if(!reduced.matches)frame=requestAnimationFrame(animate);
        });
      })();
    </script>
    """

    @staticmethod
    def _sidebar(request):
        if not getattr(request.user, "is_authenticated", False):
            return ""

        from portal.models import ToolAccess

        allowed = set(ToolAccess.objects.filter(user=request.user).values_list("tool", flat=True))
        if request.user.is_superuser:
            allowed = {"email", "scraper", "crm"}

        items = [("/", "Home", "H", request.path == "/", True)]
        for key, url, title, icon in (
            ("email", "/email/", "Email", "E"),
            ("scraper", "/scraper/", "Web Scraper", "W"),
            ("crm", "/crm/", "CRM", "C"),
        ):
            if key in allowed:
                active = request.path.startswith(url)
                items.append((url, title, icon, active, True))

        links = []
        for url, title, icon, active, _ in items:
            links.append(
                f'<a class="app-nav-link{" is-active" if active else ""}" href="{url}"><span class="app-nav-icon">{icon}</span><span>{title}</span></a>'
            )
            if title == "CRM" and active:
                from crm.models import CRMConfiguration

                configuration = CRMConfiguration.objects.filter(owner=request.user).first()
                modules = set(configuration.modules) if configuration else {
                    key for key, _ in CRMConfiguration.MODULES
                }
                subitems = [
                    ("/crm/", "Dashboard", None),
                    ("/crm/customize/", "Customize CRM", None),
                ]
                module_links = (
                    ("contacts", "/crm/contacts/", "Contacts"),
                    ("tags", "/crm/tags/", "Tags"),
                    ("segments", "/crm/segments/", "Segments"),
                    ("attendance", "/crm/attendance/", "Attendance"),
                    ("attendance", "/crm/attendance/members/add/", "+ Add member"),
                    ("transactions", "/crm/transactions/", "Sales & Purchases"),
                    ("import_export", "/crm/import/csv/", "Import"),
                    ("import_export", "/crm/export/csv/", "Export"),
                )
                subitems.extend(
                    (href, label, module)
                    for module, href, label in module_links
                    if module in modules
                )
                links.append(
                    '<div class="app-subnav">'
                    + "".join(
                        f'<a class="{"is-current" if request.path == href else ""}" href="{href}">{label}</a>'
                        for href, label, _ in subitems
                    )
                    + "</div>"
                )
        links = "".join(links)
        username = request.user.get_short_name() or request.user.get_username()
        initial = (username[:1] or "U").upper()
        return f'''
          <button id="mobile-menu-toggle" class="app-menu-button" type="button" aria-label="Open navigation menu" aria-controls="app-sidebar" aria-expanded="false"><span></span><span></span><span></span></button>
          <div id="app-menu-backdrop"></div>
          <aside id="app-sidebar" class="app-sidebar" aria-label="Main navigation">
            <div class="app-brand"><span class="app-brand-mark">A</span><span>Automation Tools</span></div>
            <nav class="app-nav">{links}</nav>
            <div class="app-sidebar-spacer"></div>
            <div class="app-profile"><span class="app-avatar">{initial}</span><span>{username}<small>Workspace</small></span></div>
            <div class="app-sidebar-bottom"><button id="automation-theme-toggle" type="button"><span>Aa</span><span>Appearance</span></button><a href="/logout/"><span>&#8599;</span><span>Log out</span></a></div>
          </aside>
        '''

    def process_response(self, request, response):
        if "text/html" not in response.get("Content-Type", "") or not hasattr(response, "content"):
            return response

        body = response.content.decode(response.charset or "utf-8")
        if "automation-theme-toggle" in body or "</body>" not in body:
            return response

        sidebar = self._sidebar(request)
        if not sidebar:
            standalone = '<button id="automation-theme-toggle" class="standalone-theme-toggle" type="button">Appearance</button>'
            if request.path != "/login/":
                standalone += '<a class="tool-back" href="/" aria-label="Back to all tools">&#8592; All tools</a>'
            sidebar = standalone

        body = body.replace("</head>", self.STYLE_SCRIPT + "</head>", 1)
        body = body.replace("<body>", '<body><canvas id="ambient-particles" aria-hidden="true"></canvas>' + sidebar, 1)
        response.content = body.encode(response.charset or "utf-8")
        response["Content-Length"] = str(len(response.content))
        return response
