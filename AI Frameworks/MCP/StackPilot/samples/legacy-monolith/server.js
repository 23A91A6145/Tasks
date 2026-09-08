const express = require('express');
const { Pool } = require('pg');
const jwt = require('jsonwebtoken');

const app = express();
const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://postgres:postgres@localhost:5432/ecommerce'
});

app.use(express.json());

// Auth Routes
app.post('/api/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await pool.query('SELECT * FROM users WHERE email = $1', [email]);
  if (!user.rows[0]) return res.status(401).json({ error: 'Invalid credentials' });
  const token = jwt.sign({ id: user.rows[0].id }, 'UNSECURE_DEFAULT_SECRET_123');
  res.json({ token });
});

// Orders Monolithic Route with Direct Foreign Key Joins
app.post('/api/orders', async (req, res) => {
  const { userId, items } = req.body;
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    const orderRes = await client.query('INSERT INTO orders (user_id, total_cents) VALUES ($1, $2) RETURNING id', [userId, 5000]);
    const orderId = orderRes.rows[0].id;
    for (const item of items) {
      await client.query('INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents) VALUES ($1, $2, $3, $4)', [orderId, item.productId, item.qty, item.price]);
      await client.query('UPDATE products SET inventory_count = inventory_count - $1 WHERE id = $2', [item.qty, item.productId]);
    }
    await client.query('COMMIT');
    res.json({ success: true, orderId });
  } catch (err) {
    await client.query('ROLLBACK');
    res.status(500).json({ error: err.message });
  } finally {
    client.release();
  }
});

app.listen(3000, () => console.log('Monolith running on port 3000'));
