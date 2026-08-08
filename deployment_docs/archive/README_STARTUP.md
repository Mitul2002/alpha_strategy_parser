# 🚀 Alpha Strategy Parser - Startup Guide

## 🎯 **One Command to Rule Them All!**

### **Linux/Mac (Recommended)**
```bash
./start_app.sh
```

### **Windows**
```bash
start_app.bat
```

### **From Any Directory**
```bash
cd /path/to/alpha_strategy_parser && ./start_app.sh
```

## 🔧 **What the Startup Script Does**

1. ✅ **Checks Prerequisites** - Virtual environment, dependencies, etc.
2. 🌐 **Starts FastAPI Backend** - Runs on http://127.0.0.1:8000
3. 🎨 **Starts Vue.js Frontend** - Runs on http://localhost:5173
4. 🔍 **Health Checks** - Verifies both services are running
5. 🛑 **Clean Shutdown** - Stops all services when you press Ctrl+C

## 🌐 **Access Your App**

Once started, open your browser to:
- **🎨 Frontend**: http://localhost:5173
- **🌐 Backend API**: http://127.0.0.1:8000
- **📚 API Documentation**: http://127.0.0.1:8000/docs

## 💡 **Quick Test**

1. Open http://localhost:5173
2. Enter strategy: `rsi(close, 14) > 70`
3. Click "Execute Strategy"
4. See beautiful results! 🎉

## 🛑 **Stopping the App**

- **Linux/Mac**: Press `Ctrl+C` in the terminal
- **Windows**: Close the command windows

## 🔧 **Troubleshooting**

### **If Backend Fails to Start:**
```bash
cd webapi
source ../venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate        # Windows
python app.py
```

### **If Frontend Fails to Start:**
```bash
cd alpha-strategy-frontend
npm run dev
```

### **If Dependencies Missing:**
```bash
# Backend
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd alpha-strategy-frontend
npm install
```

## 🎉 **You're All Set!**

Just run `./start_app.sh` and enjoy your beautiful trading strategy parser! 🚀📈 