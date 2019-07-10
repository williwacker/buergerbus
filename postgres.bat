@echo off
c: 
cd "Program Files\PostgreSQL\10\bin\"
start psql -d postgres -U postgres
exit