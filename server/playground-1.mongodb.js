/* global use, db */
// MongoDB Playground
// Use Ctrl+Space inside a snippet or a string literal to trigger completions.

// The current database to use.
use('jobs');

// Create a new document in the collection.
db.getCollection('jobs').insertOne({
  url: 'https://luova.club',
  job_type: 'DDoS',
  done: false,
  priority: 3
});
