# 🏠 Vastu Floor Plan Generator - Web Application

A beautiful, web-based floor plan generator that creates Vastu-compliant layouts using Binary Space Partitioning (BSP) algorithm.

## ✨ Features

- **Interactive Web Interface**: Modern, responsive design with gradient backgrounds
- **Real-time Generation**: Create floor plans instantly with custom dimensions
- **Multiple Entrance Options**: North, East, West, or Random
- **Detailed Statistics**: View room areas, coverage, and dimensions
- **Download Capability**: Save generated floor plans as PNG images
- **Vastu Compliance**: Follows traditional Vastu principles
- **9 Layout Variations**: Different layouts for each entrance direction
- **Zero White Space**: Complete space utilization with BSP algorithm

## 📋 Requirements

- Python 3.8 or higher
- pip (Python package manager)

## 🚀 Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

### Step 3: Open in Browser

Navigate to: **http://localhost:5000**

## 🎯 How to Use

1. **Set Plot Dimensions**
   - Enter width (15-100 units)
   - Enter height (15-100 units)

2. **Choose Entrance Direction**
   - Random (recommended for variety)
   - North
   - East
   - West

3. **Generate Floor Plan**
   - Click "Generate Floor Plan" button
   - Wait for the AI to create your layout

4. **View Results**
   - See the generated floor plan
   - Check room statistics
   - Review room details and areas

5. **Download**
   - Click "Download Floor Plan" to save as PNG

## 📊 Features Breakdown

### Room Types
- ✅ Sitout (entrance area)
- ✅ Parking
- ✅ Living Room
- ✅ 2 Bedrooms (each with attached bathroom)
- ✅ Kitchen
- ✅ Dining
- ✅ Hallway (central circulation)
- ✅ Storage (fills remaining space)

### Door Placement
- 🚪 Main entrance door (at Sitout)
- 🚪 Bedroom doors (automatic positioning)
- 🎨 Dark brown color (#5C4033)
- 📐 Automatic size scaling

## 🎨 Color Scheme

- **Sitout**: Very light gray
- **Parking**: Light gray
- **Living Room**: Very light blue
- **Bedroom 1**: Very light pink
- **Bedroom 2**: Light lemon
- **Bathrooms**: Very light cyan
- **Kitchen**: Very light yellow
- **Dining**: Very light green
- **Hallway**: White
- **Storage**: Light cornsilk

## 🛠️ Technical Details

### Backend
- **Framework**: Flask
- **Algorithm**: Binary Space Partitioning (BSP)
- **Rendering**: Matplotlib
- **Image Format**: PNG (Base64 encoded)

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern gradients, animations
- **JavaScript**: Vanilla JS (no frameworks)
- **Responsive**: Works on desktop and mobile

## 📁 File Structure

```
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend HTML/CSS/JS
└── README.md             # This file
```

## 🔧 Customization

### Change Port
Edit `app.py` line:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

### Modify Colors
Edit the `colors` dictionary in `app.py`:
```python
self.colors = {
    'sitout': '#YOUR_COLOR',
    'parking': '#YOUR_COLOR',
    # ...
}
```

### Adjust Layout Algorithms
Modify the `_generate_*_layout_*` methods in the `FloorPlanGenerator` class.

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

### Matplotlib Backend Issues
If you get display errors, ensure the backend is set to 'Agg':
```python
import matplotlib
matplotlib.use('Agg')
```

### Module Not Found
Reinstall dependencies:
```bash
pip install --upgrade -r requirements.txt
```

## 📝 API Endpoint

### POST /generate

**Request:**
```json
{
  "width": 30,
  "height": 30,
  "entrance": "North"
}
```

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "entrance": "North",
  "stats": {
    "total_rooms": 10,
    "total_doors": 3,
    "total_area": 900,
    "plot_area": 900,
    "coverage": 100.0,
    "rooms": [...]
  }
}
```

## 🌟 Future Enhancements

- [ ] Export to PDF format
- [ ] 3D floor plan view
- [ ] Furniture placement suggestions
- [ ] Cost estimation
- [ ] Multiple floor support
- [ ] User accounts and saved designs
- [ ] Share designs via link

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Developer

Created with ❤️ using Python, Flask, and Matplotlib

---

**Enjoy creating beautiful floor plans! 🏡**
