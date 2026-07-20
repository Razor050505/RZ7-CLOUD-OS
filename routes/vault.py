<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Vault - RZ7 CLOUD OS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #ffffff; --bg-secondary: #f8f9fa; --text-primary: #212529;
            --text-muted: #6c757d; --border-color: #dee2e6; --card-bg: #ffffff;
            --accent-color: #0d6efd;
        }
        [data-theme="dark"] {
            --bg-primary: #121212; --bg-secondary: #1e1e1e; --text-primary: #e0e0e0;
            --text-muted: #a0a0a0; --border-color: #333333; --card-bg: #1e1e1e;
            --accent-color: #4dabf7;
        }
        body { background-color: var(--bg-primary); color: var(--text-primary); min-height: 100vh; transition: all 0.3s ease; }
        .sidebar { background-color: var(--bg-secondary); min-height: 100vh; padding-top: 20px; border-right: 1px solid var(--border-color); }
        .nav-link { color: var(--text-muted); margin-bottom: 5px; border-radius: 5px; }
        .nav-link:hover, .nav-link.active { background-color: var(--accent-color); color: white !important; }
        .card-custom { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; color: var(--text-primary); }
        .vault-item { padding: 15px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        .vault-item:last-child { border-bottom: none; }
        .masked-key { font-family: monospace; background: var(--bg-secondary); padding: 4px 8px; border-radius: 4px; font-size: 0.9em; letter-spacing: 1px; }
        .theme-toggle { cursor: pointer; padding: 8px 12px; border-radius: 5px; border: 1px solid var(--border-color); background: transparent; color: var(--text-primary); width: 100%; text-align: left; margin-top: 10px; }
        .theme-toggle:hover { background-color: var(--border-color); }
        .toast-container { position: fixed; bottom: 20px; right: 20px; z-index: 1050; }
        
        /* Modal Dark Mode Fix */
        .modal-content { background-color: var(--card-bg); color: var(--text-primary); border: 1px solid var(--border-color); }
        .modal-header, .modal-footer { border-color: var(--border-color); }
        .form-control { background-color: var(--bg-secondary); color: var(--text-primary); border-color: var(--border-color); }
        .form-control:focus { background-color: var(--bg-secondary); color: var(--text-primary); border-color: var(--accent-color); box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25); }
        .btn-close { filter: invert(var(--invert-val, 0)); }
        [data-theme="dark"] .btn-close { --invert-val: 1; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2 sidebar d-none d-md-block">
                <h4 class="text-center mb-4">☁ RZ7 CLOUD OS</h4>
                <p class="text-center text-muted small">v0.4 Alpha</p>
                <div class="d-flex align-items-center mb-4 px-3">
                    <span class="badge bg-primary me-2"></span>
                    <span>{{ current_user.id }}</span>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link" href="/dashboard"> Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> My Projects</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> AI Assistant</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> APK Manager</a></li>
                    <li class="nav-item"><a class="nav-link" href="/storage">☁ Cloud Storage</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/vault"> API Vault</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">💻 Terminal</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> Monitoring</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> Settings</a></li>
                </ul>
                <button id="themeToggle" class="theme-toggle mt-4"> Dark Mode</button>
                <hr class="border-secondary mt-4">
                <a href="/logout" class="btn btn-outline-danger w-100 mt-3"> Logout</a>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10 p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>🔑 API Vault Manager</h3>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addVaultModal">+ Tambah API Key</button>
                </div>
                
                <div class="card card-custom">
                    <div class="card-header border-0 bg-transparent">
                        <h5 class="mb-0">Stored Credentials</h5>
                    </div>
                    <div class="card-body p-0" id="vaultList">
                        {% if entries %}
                            {% for entry in entries %}
                            <div class="vault-item">
                                <div>
                                    <strong>{{ entry.name }}</strong>
                                    <br><small class="text-muted">{{ entry.created_at }}</small>
                                </div>
                                <div class="d-flex align-items-center gap-2">
                                    <span class="masked-key">{{ entry.masked_key }}</span>
                                    <button onclick="revealKey('{{ entry.id }}')" class="btn btn-sm btn-outline-info" title="Salin Kunci">📋</button>
                                    <button onclick="deleteEntry('{{ entry.id }}')" class="btn btn-sm btn-outline-danger" title="Hapus">🗑️</button>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="text-center p-4 text-muted">Belum ada API Key yang disimpan</div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Tambah API Key -->
    <div class="modal fade" id="addVaultModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Tambah API Key Baru</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Nama Layanan</label>
                        <input type="text" class="form-control" id="vaultName" placeholder="Contoh: OpenAI API, Render Token">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">API Key / Secret</label>
                        <textarea class="form-control" id="vaultKey" rows="3" placeholder="Tempel API key disini..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Batal</button>
                    <button type="button" class="btn btn-primary" onclick="saveVault()">Simpan Terenkripsi</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast-container">
        <div id="liveToast" class="toast align-items-center text-white bg-success border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body" id="toastMessage">Berhasil!</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    </div>

<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Vault - RZ7 CLOUD OS</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #ffffff; --bg-secondary: #f8f9fa; --text-primary: #212529;
            --text-muted: #6c757d; --border-color: #dee2e6; --card-bg: #ffffff;
            --accent-color: #0d6efd;
        }
        [data-theme="dark"] {
            --bg-primary: #121212; --bg-secondary: #1e1e1e; --text-primary: #e0e0e0;
            --text-muted: #a0a0a0; --border-color: #333333; --card-bg: #1e1e1e;
            --accent-color: #4dabf7;
        }
        body { background-color: var(--bg-primary); color: var(--text-primary); min-height: 100vh; transition: all 0.3s ease; }
        .sidebar { background-color: var(--bg-secondary); min-height: 100vh; padding-top: 20px; border-right: 1px solid var(--border-color); }
        .nav-link { color: var(--text-muted); margin-bottom: 5px; border-radius: 5px; }
        .nav-link:hover, .nav-link.active { background-color: var(--accent-color); color: white !important; }
        .card-custom { background-color: var(--card-bg); border: 1px solid var(--border-color); border-radius: 10px; color: var(--text-primary); }
        .vault-item { padding: 15px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; }
        .vault-item:last-child { border-bottom: none; }
        .masked-key { font-family: monospace; background: var(--bg-secondary); padding: 4px 8px; border-radius: 4px; font-size: 0.9em; letter-spacing: 1px; }
        .theme-toggle { cursor: pointer; padding: 8px 12px; border-radius: 5px; border: 1px solid var(--border-color); background: transparent; color: var(--text-primary); width: 100%; text-align: left; margin-top: 10px; }
        .theme-toggle:hover { background-color: var(--border-color); }
        .toast-container { position: fixed; bottom: 20px; right: 20px; z-index: 1050; }
        
        /* Modal Dark Mode Fix */
        .modal-content { background-color: var(--card-bg); color: var(--text-primary); border: 1px solid var(--border-color); }
        .modal-header, .modal-footer { border-color: var(--border-color); }
        .form-control { background-color: var(--bg-secondary); color: var(--text-primary); border-color: var(--border-color); }
        .form-control:focus { background-color: var(--bg-secondary); color: var(--text-primary); border-color: var(--accent-color); box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25); }
        .btn-close { filter: invert(var(--invert-val, 0)); }
        [data-theme="dark"] .btn-close { --invert-val: 1; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <!-- Sidebar -->
            <div class="col-md-3 col-lg-2 sidebar d-none d-md-block">
                <h4 class="text-center mb-4">☁ RZ7 CLOUD OS</h4>
                <p class="text-center text-muted small">v0.4 Alpha</p>
                <div class="d-flex align-items-center mb-4 px-3">
                    <span class="badge bg-primary me-2"></span>
                    <span>{{ current_user.id }}</span>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item"><a class="nav-link" href="/dashboard"> Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> My Projects</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> AI Assistant</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> APK Manager</a></li>
                    <li class="nav-item"><a class="nav-link" href="/storage">☁ Cloud Storage</a></li>
                    <li class="nav-item"><a class="nav-link active" href="/vault"> API Vault</a></li>
                    <li class="nav-item"><a class="nav-link" href="#">💻 Terminal</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> Monitoring</a></li>
                    <li class="nav-item"><a class="nav-link" href="#"> Settings</a></li>
                </ul>
                <button id="themeToggle" class="theme-toggle mt-4"> Dark Mode</button>
                <hr class="border-secondary mt-4">
                <a href="/logout" class="btn btn-outline-danger w-100 mt-3"> Logout</a>
            </div>

            <!-- Main Content -->
            <div class="col-md-9 col-lg-10 p-4">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h3>🔑 API Vault Manager</h3>
                    <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addVaultModal">+ Tambah API Key</button>
                </div>
                
                <div class="card card-custom">
                    <div class="card-header border-0 bg-transparent">
                        <h5 class="mb-0">Stored Credentials</h5>
                    </div>
                    <div class="card-body p-0" id="vaultList">
                        {% if entries %}
                            {% for entry in entries %}
                            <div class="vault-item">
                                <div>
                                    <strong>{{ entry.name }}</strong>
                                    <br><small class="text-muted">{{ entry.created_at }}</small>
                                </div>
                                <div class="d-flex align-items-center gap-2">
                                    <span class="masked-key">{{ entry.masked_key }}</span>
                                    <button onclick="revealKey('{{ entry.id }}')" class="btn btn-sm btn-outline-info" title="Salin Kunci">📋</button>
                                    <button onclick="deleteEntry('{{ entry.id }}')" class="btn btn-sm btn-outline-danger" title="Hapus">🗑️</button>
                                </div>
                            </div>
                            {% endfor %}
                        {% else %}
                            <div class="text-center p-4 text-muted">Belum ada API Key yang disimpan</div>
                        {% endif %}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal Tambah API Key -->
    <div class="modal fade" id="addVaultModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Tambah API Key Baru</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Nama Layanan</label>
                        <input type="text" class="form-control" id="vaultName" placeholder="Contoh: OpenAI API, Render Token">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">API Key / Secret</label>
                        <textarea class="form-control" id="vaultKey" rows="3" placeholder="Tempel API key disini..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Batal</button>
                    <button type="button" class="btn btn-primary" onclick="saveVault()">Simpan Terenkripsi</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast-container">
        <div id="liveToast" class="toast align-items-center text-white bg-success border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body" id="toastMessage">Berhasil!</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    </div>

