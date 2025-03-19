import os
import subprocess
import sys
from pathlib import Path

def generate_self_signed_cert():
    """Generate self-signed SSL certificates for development"""
    print("Generating self-signed SSL certificates...")
    
    cert_dir = Path("./certs")
    cert_dir.mkdir(exist_ok=True)
    
    key_path = cert_dir / "key.pem"
    cert_path = cert_dir / "cert.pem"
    
    # Only generate certificates if they don't exist
    if not key_path.exists() or not cert_path.exists():
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-nodes',
            '-out', str(cert_path), '-keyout', str(key_path),
            '-days', '365', '-subj', '/CN=localhost'
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"SSL certificates generated successfully at {cert_dir}")
        except subprocess.CalledProcessError as e:
            print(f"Error generating SSL certificates: {e}")
            sys.exit(1)
    else:
        print("SSL certificates already exist")
    
    return str(key_path), str(cert_path)

if __name__ == "__main__":
    key_path, cert_path = generate_self_signed_cert()
    
    # Run the application with SSL
    import uvicorn
    
    print(f"Starting FastAPI application with HTTPS on port 8443")
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8443, 
        ssl_keyfile=key_path, 
        ssl_certfile=cert_path,
        reload=True
    )