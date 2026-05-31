use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::Manager;

struct PythonBackend(Mutex<Option<Child>>);

#[tauri::command]
fn start_backend(state: tauri::State<PythonBackend>) -> Result<String, String> {
    let mut child = state.0.lock().map_err(|e| e.to_string())?;
    if child.is_some() {
        return Ok("Backend already running".into());
    }

    let backend_dir = std::env::current_dir()
        .map_err(|e| e.to_string())?
        .parent()
        .map(|p| p.join("backend"))
        .ok_or("Cannot resolve backend path")?;

    let process = Command::new("python")
        .arg("-m")
        .arg("uvicorn")
        .arg("main:app")
        .arg("--host")
        .arg("127.0.0.1")
        .arg("--port")
        .arg("8899")
        .current_dir(&backend_dir)
        .spawn()
        .map_err(|e| format!("Failed to start backend: {}", e))?;

    *child = Some(process);
    log::info!("Python backend started");
    Ok("Backend started".into())
}

#[tauri::command]
fn stop_backend(state: tauri::State<PythonBackend>) -> Result<String, String> {
    let mut child = state.0.lock().map_err(|e| e.to_string())?;
    if let Some(mut proc) = child.take() {
        proc.kill().map_err(|e| format!("Failed to kill backend: {}", e))?;
        log::info!("Python backend stopped");
        Ok("Backend stopped".into())
    } else {
        Ok("No backend running".into())
    }
}

#[tauri::command]
fn backend_status(state: tauri::State<PythonBackend>) -> Result<String, String> {
    let child = state.0.lock().map_err(|e| e.to_string())?;
    match child.as_ref() {
        Some(_) => Ok("running".into()),
        None => Ok("stopped".into()),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .setup(|app| {
            if cfg!(debug_assertions) {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build(),
                )?;
            }
            app.manage(PythonBackend(Mutex::new(None)));
            log::info!("ClipOS app initialized");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            start_backend,
            stop_backend,
            backend_status,
        ])
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { .. } = event {
                if let Some(state) = window.try_state::<PythonBackend>() {
                    if let Ok(mut child) = state.0.lock() {
                        if let Some(mut proc) = child.take() {
                            let _ = proc.kill();
                            log::info!("Backend process cleaned up on window close");
                        }
                    }
                }
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
