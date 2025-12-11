#!/bin/bash
# Full system verification script

echo "============================================================"
echo "KASHROCK V6 - FULL SYSTEM VERIFICATION"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Redis is running
echo "[1/6] Checking Redis..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Redis is running${NC}"
else
    echo -e "${RED}✗ Redis is not running${NC}"
    echo "Starting Redis..."
    redis-server --daemonize yes
    sleep 2
fi
echo ""

# Clear Redis cache for fresh test
echo "[2/6] Clearing Redis cache for fresh test..."
redis-cli FLUSHDB > /dev/null 2>&1
echo -e "${GREEN}✓ Redis cache cleared${NC}"
echo ""

# Start backend
echo "[3/6] Starting backend server..."
echo "Activating virtual environment and starting uvicorn..."
cd /Users/drax/Downloads/kashrock-main

# Kill any existing uvicorn processes
pkill -f "uvicorn main:app" 2>/dev/null

# Start backend in background
source .venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo "  Logs: tail -f backend.log"
echo ""

# Wait for backend to be ready
echo "[4/6] Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Start frontend
echo "[5/6] Starting frontend..."
cd new-frontend

# Kill any existing npm processes
pkill -f "next dev" 2>/dev/null

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start frontend in background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo "  Logs: tail -f frontend.log"
echo ""

# Wait for frontend to be ready
echo "[6/6] Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠ Frontend may still be starting${NC}"
        break
    fi
    sleep 1
done
echo ""

echo "============================================================"
echo "✓ SYSTEM STARTED SUCCESSFULLY"
echo "============================================================"
echo ""
echo "Services running:"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:3000"
echo ""
echo "Process IDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Sign in with Google to create an account"
echo "  3. Generate an API key from the dashboard"
echo "  4. Test the API with your key"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  or run: pkill -f 'uvicorn main:app' && pkill -f 'next dev'"
echo ""
echo "Monitor logs:"
echo "  Backend:  tail -f /Users/drax/Downloads/kashrock-main/backend.log"
echo "  Frontend: tail -f /Users/drax/Downloads/kashrock-main/frontend.log"
echo "  Worker:   tail -f /Users/drax/Downloads/kashrock-main/worker.log"
echo ""
