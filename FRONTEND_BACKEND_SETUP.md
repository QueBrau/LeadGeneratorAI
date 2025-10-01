# Frontend-Backend Connection Guide

## 🚀 Quick Start

### Option 1: Use the Development Startup Script (Recommended)
```bash
python start_dev.py
```
Choose option 3 to start both servers automatically.

### Option 2: Manual Startup

#### Start Backend (Terminal 1):
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Flask API server
python api_server.py
```
✅ Backend will run on: http://localhost:5000

#### Start Frontend (Terminal 2):
```bash
# Navigate to frontend directory
cd lead-finder-frontend

# Install npm dependencies (first time only)
npm install

# Start React development server
npm start
```
✅ Frontend will run on: http://localhost:3000

## 🔌 API Endpoints

The backend provides these REST API endpoints:

- `GET /api/health` - Health check
- `GET /api/config` - Get current configuration
- `POST /api/search` - Start a new lead search
- `GET /api/search/{id}/status` - Get search progress
- `GET /api/search/{id}/results` - Get search results
- `POST /api/search/{id}/cancel` - Cancel running search
- `GET /api/leads` - Get all qualified leads
- `GET /api/leads/{id}` - Get specific lead details

## 🌐 How It Works

1. **React Frontend** (port 3000) sends search requests to Flask backend
2. **Flask Backend** (port 5000) processes searches using your Python lead finder
3. **Real-time Updates** via polling - frontend checks search progress every 3 seconds
4. **Results Display** - qualified leads appear in real-time as they're found

## 🔧 Configuration

### Backend Configuration (.env file):
```env
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_api_key_here  # Optional - for better results
GOOGLE_CSE_ID=your_custom_search_engine_id_here  # Optional
LOCATION=Durham, NC
```

### Frontend Configuration:
The frontend automatically connects to `http://localhost:5000/api` by default.

## 🐛 Troubleshooting

### "Unable to connect to backend"
- Make sure the Flask server is running on port 5000
- Check if any firewall is blocking the connection
- Verify the backend shows "CORS enabled for React frontend"

### "Search not working"
- Ensure your OpenAI API key is set in the `.env` file
- Check the backend terminal for error messages
- For better results, set up the optional Google Custom Search API

### "Frontend won't start"
- Make sure Node.js and npm are installed
- Run `npm install` in the `lead-finder-frontend` directory
- Delete `node_modules` and run `npm install` again if issues persist

## 📊 Features

- ✅ **Real-time Search Progress** - See search status and progress
- ✅ **Live Results** - Results appear as they're found
- ✅ **Lead History** - Tab to view all previously found leads
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Error Handling** - Graceful error messages and recovery
- ✅ **Free APIs** - Uses Reddit API directly + optional Google Custom Search

## 🎯 Next Steps

1. **Start both servers** using the methods above
2. **Open your browser** to http://localhost:3000
3. **Enter search terms** (e.g., "painter", "renovation")
4. **Click "Start Search"** and watch results appear in real-time!
5. **View Lead History** tab to see all qualified leads

Your full-stack lead generator is now connected and ready to use! 🎉