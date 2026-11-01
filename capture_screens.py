"""
Script to capture pixel-perfect screenshots of every screen at Desktop (1280px)
and Mobile (390px) width using Chrome headless.
"""
import subprocess
import time
from pathlib import Path

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
OUTPUT_DIR = Path(r"C:\Users\dcsjm\OneDrive\Documents\Desktop\Bill Bndhu\docs\screenshots")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HTML_FILE = Path(r"C:\Users\dcsjm\OneDrive\Documents\Desktop\Bill Bndhu\frontend\index.html").resolve()

SCREENS = ["home", "scan", "review", "done", "bills", "reports", "settings"]

def capture():
    # Read the base HTML
    base_html = HTML_FILE.read_text(encoding="utf-8")

    for screen in SCREENS:
        # Create a temporary variant of HTML that loads this screen directly
        mod_html = base_html.replace(
            "let currentScreen = 'home';",
            f"let currentScreen = '{screen}';"
        ).replace(
            'document.addEventListener("DOMContentLoaded", () => {\n      setLanguage(\'hi\');\n      setSliderPercentage(50);\n    });',
            f'document.addEventListener("DOMContentLoaded", () => {{\n      setLanguage(\'hi\');\n      setSliderPercentage(50);\n      navigate(\'{screen}\');\n      if (\'{screen}\' === \'scan\') tryDemoBill();\n    }});'
        )

        tmp_file = OUTPUT_DIR / f"tmp_{screen}.html"
        tmp_file.write_text(mod_html, encoding="utf-8")
        url = tmp_file.as_uri()

        # Desktop (1280 x 900)
        desk_shot = OUTPUT_DIR / f"{screen}_desktop.png"
        cmd_desk = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=1280,900",
            f"--screenshot={str(desk_shot)}",
            url
        ]
        subprocess.run(cmd_desk, check=True)

        # Mobile (390 x 844 - iPhone 12/13/14 standard width)
        mob_shot = OUTPUT_DIR / f"{screen}_mobile_390px.png"
        cmd_mob = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--hide-scrollbars",
            "--window-size=390,844",
            f"--screenshot={str(mob_shot)}",
            url
        ]
        subprocess.run(cmd_mob, check=True)

        # Clean up temp html
        tmp_file.unlink(missing_ok=True)
        print(f"Captured {screen} (Desktop + 390px Mobile)")

if __name__ == "__main__":
    capture()
    print("All screenshots successfully captured in docs/screenshots/")

