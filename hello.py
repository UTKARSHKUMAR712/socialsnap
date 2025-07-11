import webview

webview.create_window("Hello Utkarsh 👋", html="<h1>PyWebView is working!</h1>")
webview.start(gui='qt')  # start AFTER window is created