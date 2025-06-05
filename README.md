# PyPositron
### **PyPositron is currently in alpha stage.** It is not yet ready for production use, but you can try it out and contribute to its development. See more in [Contributing](#contributing).
**PyPositron** is a Python-powered desktop app framework that lets you build cross-platform apps using HTML, CSS, and Python—just like Electron, but with Python as the backend. Write your UI in HTML/CSS, add interactivity with Python, and run your app natively!


## Features

- Build desktop apps using HTML and CSS.
- Use Python for backend and frontend logic. (with support for both Python and JS)
- Use any HTML/CSS framework (like Bootstrap, Tailwind, etc.) for your UI.
- Use any HTML builder UI for your app (like Bootstrap Studio, Pinegrow, etc)
- Use JS for compatibility with existing HTML/CSS frameworks.
- Use AI tools for generating your UI without needing proprietary system prompts- simply tell it to generate HTML/CSS/JS UI for your app.
- Virtual environment support.
- Efficient installer creation for easy distribution (that does not exist yet)
(The installer automatically finds an existing browser instead of installing a new one for every app like Electron.JS).

## Why PyPositron?
Compared to Electron and other Python frameworks (like PyQt)-
| Feature | PyPositron | Electron | PyQt |
|---------|------------|----------|------|
| Language | Python | **JavaScript, C, C++, etc** | Python |
| UI Frameworks | Only frontend HTML/CSS/JS | **Any Web technologies** | Qt Widgets |
| Packaging | **Efficient installer or standalone executable (not yet implemented)** | Electron Builder | PyInstaller etc |
| Performance | **Lightweight** | Heavyweight | **Lightweight** |
| AI Compatibility | **Yes** | **Yes\*** | No\* |
| Compatibility | All frontend HTML/CSS/JS frameworks | **All frontend and backend HTML/CSS/JS frameworks and web technologies** | Limited to Qt |

\* maybe

## Quick Start

### 1. Create a New Project
Install PyPositron if not already installed:
```bash
pip install py-positron 
```
Them create a new project using the CLI:
```bash
positron create
# Follow the prompts to set up your project
```
There should be directories in this structure-

```
your_app/
├── backend
│   └── main.py
├── frontend/
│   └── index.html
├── [win/linux]venv/ # If created
│   └──...
├── LICENSE #MIT by default
├── config.json
└── ...
```

- **backend/main.py**: Entry point for your app. 
- **frontend/index.html**: Your app's UI (HTML/CSS/inline Python/JS). 
- **winvenv/** or **linuxvenv/**:: (Optional) Virtual environment for dependencies.

### 2. Run Your App

```bash
positron start
``` 

This should open up a window with a checkmark and a button.

## CLI Commands

| Command                                  | Description                                                   |
|------------------------------------------|---------------------------------------------------------------|
| `positron create`                        | Create a new PyPositron project (interactive setup).          |
| `positron start [--executable <python>]` | Run your PyPositron app (optionally specify Python interpreter).|
| `positron install <package>`             | Install a Python package into the project venv.               |
| `positron venv`                          | Create a virtual environment inside your project folder.      |


## Documentation & Resources

- [Official Tutorial & Docs](https://github.com/itzmetanjim/py-positron/wiki)

## License

GNU AGPL v3 License. See [LICENSE](LICENSE) for details.

## Contributing

This project is in alpha stage. Contributions are welcome. Things to do-
* [ ] Make documentation and README that is not AI-generated
* [ ] Add more examples and tutorials
* [ ] Make the installer/executable creation system
* [ ] Test on Linux
* [ ] Add support for MacOS
* [ ] Add building and packaging features (like converting to executables/installers that can run on any system without Python installed)
* [ ] Optimize performance.
