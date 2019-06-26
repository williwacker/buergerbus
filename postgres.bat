@echo off
c: 
cd "Program Files\PostgreSQL\10\bin\"
start psql -d postgresql -U postgres
exit