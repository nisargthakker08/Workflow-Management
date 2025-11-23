// backend/server.js
import express from 'express';
import cors from 'cors';
import multer from 'multer';
import XLSX from 'xlsx';
import sqlite3 from 'sqlite3';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import bodyParser from 'body-parser';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ 
  storage,
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['.xlsx', '.xls', '.csv'];
    const fileExt = file.originalname.toLowerCase().slice(-5);
    if (allowedTypes.some(ext => fileExt.includes(ext))) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only Excel and CSV files are allowed.'));
    }
  },
  limits: { fileSize: 50 * 1024 * 1024 } // 50MB
});

// Initialize SQLite database
const db = new sqlite3.Database('./arms_workflow.db', (err) => {
  if (err) {
    console.error('Error opening database:', err);
  } else {
    console.log('Connected to SQLite database');
    initializeDatabase();
  }
});

function initializeDatabase() {
  db.run(`
    CREATE TABLE IF NOT EXISTS tasks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT NOT NULL,
      description TEXT,
      status TEXT DEFAULT 'Pending',
      priority TEXT DEFAULT 'Medium',
      assigned_to TEXT,
      created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
      due_date DATETIME,
      row_data TEXT
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS uploads (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      filename TEXT NOT NULL,
      sheets_loaded TEXT,
      upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
      record_count INTEGER
    )
  `);
}

// Routes
app.get('/api/health', (req, res) => {
  res.json({ status: 'Server is running!' });
});

// Upload Excel file
app.post('/api/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const { selectedSheets } = req.body;
    const sheets = selectedSheets ? JSON.parse(selectedSheets) : [];
    
    const workbook = XLSX.readFile(req.file.path);
    const sheetData = {};
    let allData = [];

    const sheetsToProcess = sheets.length > 0 ? sheets : workbook.SheetNames;

    sheetsToProcess.forEach(sheetName => {
      if (workbook.Sheets[sheetName]) {
        const worksheet = workbook.Sheets[sheetName];
        const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
        sheetData[sheetName] = jsonData;
        
        // Convert to objects for combined analysis (skip header row if exists)
        const objects = XLSX.utils.sheet_to_json(worksheet);
        allData = allData.concat(objects);
      }
    });

    // Save upload record
    const stmt = db.prepare(`
      INSERT INTO uploads (filename, sheets_loaded, record_count) 
      VALUES (?, ?, ?)
    `);
    stmt.run(req.file.filename, JSON.stringify(sheetsToProcess), allData.length);
    stmt.finalize();

    res.json({
      message: 'File processed successfully',
      sheets: sheetsToProcess,
      totalRecords: allData.length,
      availableSheets: workbook.SheetNames,
      data: allData
    });

  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Error processing file: ' + error.message });
  }
});

// Get dashboard metrics
app.post('/api/metrics', (req, res) => {
  try {
    const { data } = req.body;
    
    if (!data || !Array.isArray(data)) {
      return res.status(400).json({ error: 'No data provided' });
    }

    const metrics = calculateMetrics(data);
    res.json(metrics);
  } catch (error) {
    console.error('Metrics error:', error);
    res.status(500).json({ error: 'Error calculating metrics' });
  }
});

function calculateMetrics(data) {
  if (!data || data.length === 0) {
    return getEmptyMetrics();
  }

  const df = data;
  const metrics = {
    total_pending: 0,
    open_ucc_actions: 0,
    distinct_team_members: 0,
    judgment_amount: 0,
    total_work_units: 0,
    chapter_11_cases: 0,
    chapter_7_cases: 0,
    total_judgment_entries: 0
  };

  // Total Pending
  const statusColumn = findColumn(df, ['status', 'state', 'current_status']);
  if (statusColumn) {
    metrics.total_pending = df.filter(row => 
      String(row[statusColumn] || '').toLowerCase().includes('pending')
    ).length;
  } else {
    metrics.total_pending = df.length;
  }

  // Open UCC Actions
  const uccColumn = findColumn(df, ['ucc', 'ucc_action', 'action']);
  if (uccColumn) {
    metrics.open_ucc_actions = df.filter(row =>
      String(row[uccColumn] || '').toLowerCase().includes('open')
    ).length;
  }

  // Distinct Team Members
  const analystColumn = findColumn(df, ['analyst', 'team_member', 'assigned_to']);
  if (analystColumn) {
    const analysts = new Set(df.map(row => row[analystColumn]).filter(Boolean));
    metrics.distinct_team_members = analysts.size;
  }

  // Judgment Entries
  const judgmentColumn = findColumn(df, ['judgment', 'judgment_amount', 'amount']);
  if (judgmentColumn) {
    metrics.total_judgment_entries = df.filter(row => 
      row[judgmentColumn] != null && row[judgmentColumn] !== ''
    ).length;
    metrics.judgment_amount = metrics.total_judgment_entries;
  }

  // Work Units
  const workUnitColumn = findColumn(df, ['work_units', 'units', 'work']);
  if (workUnitColumn) {
    metrics.total_work_units = df.reduce((sum, row) => {
      const value = parseFloat(row[workUnitColumn]) || 0;
      return sum + value;
    }, 0);
  } else {
    metrics.total_work_units = df.length;
  }

  // Chapter Cases
  const chapterColumn = findColumn(df, ['chapter', 'case_type', 'type']);
  if (chapterColumn) {
    metrics.chapter_11_cases = df.filter(row => 
      String(row[chapterColumn]).includes('11') || 
      String(row[chapterColumn]).toLowerCase().includes('chapter 11') ||
      String(row[chapterColumn]).toLowerCase().includes('ch 11')
    ).length;

    metrics.chapter_7_cases = df.filter(row =>
      String(row[chapterColumn]).includes('7') ||
      String(row[chapterColumn]).toLowerCase().includes('chapter 7') ||
      String(row[chapterColumn]).toLowerCase().includes('ch 7')
    ).length;
  } else {
    // Search in all string columns
    df.forEach(row => {
      Object.values(row).forEach(value => {
        const strValue = String(value).toLowerCase();
        if (strValue.includes('chapter 11') || strValue.includes('ch 11')) {
          metrics.chapter_11_cases++;
        }
        if (strValue.includes('chapter 7') || strValue.includes('ch 7')) {
          metrics.chapter_7_cases++;
        }
      });
    });
  }

  return metrics;
}

function findColumn(df, possibleNames) {
  if (df.length === 0) return null;
  const firstRow = df[0];
  return Object.keys(firstRow).find(key =>
    possibleNames.some(name => 
      key.toLowerCase().includes(name.toLowerCase())
    )
  );
}

function getEmptyMetrics() {
  return {
    total_pending: 0,
    open_ucc_actions: 0,
    distinct_team_members: 0,
    judgment_amount: 0,
    total_work_units: 0,
    chapter_11_cases: 0,
    chapter_7_cases: 0,
    total_judgment_entries: 0
  };
}

// Tasks endpoints
app.post('/api/tasks/create', (req, res) => {
  try {
    const { data } = req.body;
    const tasks = [];

    data.forEach((row, index) => {
      const task = {
        title: `Case ${index + 1}`,
        description: `Process case from row ${index + 1}`,
        status: 'Pending',
        priority: 'Medium',
        assigned_to: '',
        row_data: JSON.stringify(row)
      };

      const stmt = db.prepare(`
        INSERT INTO tasks (title, description, status, priority, assigned_to, row_data)
        VALUES (?, ?, ?, ?, ?, ?)
      `);
      
      stmt.run(
        task.title,
        task.description,
        task.status,
        task.priority,
        task.assigned_to,
        task.row_data
      );
      stmt.finalize();

      tasks.push({ ...task, id: index + 1 });
    });

    res.json({
      message: `Created ${tasks.length} tasks successfully`,
      tasks: tasks
    });
  } catch (error) {
    res.status(500).json({ error: 'Error creating tasks' });
  }
});

app.get('/api/tasks', (req, res) => {
  db.all('SELECT * FROM tasks ORDER BY created_date DESC', (err, rows) => {
    if (err) {
      res.status(500).json({ error: 'Error fetching tasks' });
    } else {
      res.json(rows);
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
  console.log(`📊 ARMS Workflow Manager Backend ready!`);
});
