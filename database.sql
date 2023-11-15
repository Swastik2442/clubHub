create table branch(
branch_id   varchar(4),
branch_name varchar(30),
constraint b_pk primary key (branch_id)
);
exec sp_columns branch;

create table student(
roll_no     varchar(11),
s_name      varchar(50),
branch_id   varchar(4),
batch int,
constraint s_pk primary key(roll_no,branch_id,batch),
constraint b_fk foreign key(branch_id) references branch
);
exec sp_columns student;

create table club(
club_id                     varchar(10),
club_name                   varchar(50) not null,
club_year                   int,
president_roll_no           varchar(11),
president_branch_id         varchar(4),
president_batch             int,
vice_president_roll_no      varchar(11),
vice_president_branch_id    varchar(4),
vice_president_batch        int,
faculty_mentor              varchar(50),
topic                       varchar(50) not null,
constraint c_pk primary key(c_id,c_year),
constraint p_fk foreign key(president_roll_no, president_branch_id, president_batch) references student(roll_no, branch_id, batch), -- Not Supported in Django
constraint vp_fk foreign key(vice_president_roll_no, vice_president_branch_id, vice_president_batch) references student(roll_no, branch_id, batch) -- Not Supported in Django
);
exec sp_columns club;