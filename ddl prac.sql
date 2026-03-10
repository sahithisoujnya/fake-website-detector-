create database sahithi;
use sahithi;
create table soujnya(
student_id int,
name_ varchar(10),
department varchar(50),
age int,
marks int
);
alter table soujnya add email varchar(50);
alter table soujnya modify name_ varchar(30);
show  tables;
desc soujnya;
rename table soujnya to students_data;
show tables;
insert into students_data values 
( 1,'anu','cse',19,85,'anu@gmail.com');
show tables;
desc students_data;
select *from students_data;
truncate table students_data;
select *from students_data;
drop table students_data;
show tables;
drop table students_data;

