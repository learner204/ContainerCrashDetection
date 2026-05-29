import subprocess
import sys

def main():
    print("🚢 Container Crash Detection System")
    print("------------------------------------")
    print("To start the backend server, run: python api_server.py")
    print("To start the frontend, navigate to /frontend and run: npm run dev")
    print("\nAttempting to start the backend server for you...")
    
    try:
        subprocess.run([sys.executable, "api_server.py"])
    except KeyboardInterrupt:
        print("\nStopping server...")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()
