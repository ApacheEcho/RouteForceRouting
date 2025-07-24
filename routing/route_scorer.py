services:
  - type: web
    name: routeforcepro
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python routing/route_scorer.py
    envVars:
      - key: PORT
        value: 5000
