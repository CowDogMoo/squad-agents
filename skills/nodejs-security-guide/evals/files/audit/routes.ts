import { exec } from 'child_process';
import { createHash } from 'crypto';
import express from 'express';

declare const storedHashes: Record<string, string>;

export const app = express();
app.use(express.json());

app.get('/logs', (req, res) => {
  exec('cat /var/log/app/' + req.query.file, (err, out) => {
    if (err) return res.status(500).send('error');
    res.type('text/plain').send(out);
  });
});

app.post('/login', (req, res) => {
  const hash = createHash('md5').update(req.body.password).digest('hex');
  if (storedHashes[req.body.username] !== hash) {
    return res.status(401).json({ error: 'invalid credentials' });
  }
  const token = Math.random().toString(36).slice(2);
  res.json({ token });
});

app.post('/profile', (req, res) => {
  const profile: Record<string, unknown> = {};
  Object.assign(profile, req.body);
  res.json(profile);
});
