#!/bin/bash

# Create a Mac app bundle for Elara Poker Calculator
echo "Creating Mac app bundle for Elara..."

# Create the app bundle structure
APP_NAME="Elara Poker Calculator"
APP_DIR="${APP_NAME}.app"
CONTENTS_DIR="${APP_DIR}/Contents"
MACOS_DIR="${CONTENTS_DIR}/MacOS"
RESOURCES_DIR="${CONTENTS_DIR}/Resources"

# Create directories
mkdir -p "$MACOS_DIR"
mkdir -p "$RESOURCES_DIR"

# Copy the entire project to Resources
echo "Copying project files..."
cp -r . "$RESOURCES_DIR/"

# Create the main executable script
cat > "$MACOS_DIR/Elara" << 'EOF'
#!/bin/bash

# Get the directory where the app bundle is located
APP_DIR="$(dirname "$0")"
PROJECT_DIR="$APP_DIR/../Resources"

# Change to the project directory
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    # Show setup dialog
    osascript -e 'display dialog "Setting up Elara for the first time. This may take a moment..." buttons {"OK"} default button "OK"'
    
    # Run setup
    ./setup.sh
    if [ $? -ne 0 ]; then
        osascript -e 'display dialog "Setup failed. Please check the Terminal for errors." buttons {"OK"} default button "OK"'
        exit 1
    fi
fi

# Start the backend server
cd backend
source venv/bin/activate
python simple_app.py &
BACKEND_PID=$!

# Wait for server to start
sleep 3

# Check if server started
if curl -s http://localhost:5000/health > /dev/null; then
    # Open frontend in browser
    open "../frontend/index.html"
    
    # Show success message
    osascript -e 'display dialog "Elara Poker Calculator is now running!" & return & return "Backend: http://localhost:5000" & return "Frontend: Opened in your browser" buttons {"OK"} default button "OK"'
    
    # Keep running
    wait $BACKEND_PID
else
    osascript -e 'display dialog "Failed to start Elara. Please check the Terminal for errors." buttons {"OK"} default button "OK"'
    exit 1
fi
EOF

# Make the executable script executable
chmod +x "$MACOS_DIR/Elara"

# Create Info.plist
cat > "$CONTENTS_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>Elara</string>
    <key>CFBundleIdentifier</key>
    <string>com.elara.poker-calculator</string>
    <key>CFBundleName</key>
    <string>Elara Poker Calculator</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
EOF

echo "Mac app bundle created: $APP_DIR"
echo ""
echo "You can now:"
echo "1. Double-click '$APP_DIR' to run Elara"
echo "2. Drag it to your Applications folder"
echo "3. Add it to your Dock for easy access"
echo ""
echo "The app will automatically:"
echo "   - Set up dependencies on first run"
echo "   - Start the backend server"
echo "   - Open the frontend in your browser"
