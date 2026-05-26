# Gunicorn Setup

## Command

```
 gunicorn -w 3 -k gthread -t 120 -b 0.0.0.0:8000 wsgi:app
```

## Tuning

- Increase workers for CPU-bound workloads.
- Use `gthread` for mixed I/O + CPU.
- Adjust timeout if weather API calls are slow.
