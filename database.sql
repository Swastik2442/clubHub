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
club_logo_url               varchar(50),
president_roll_no           varchar(11),
president_branch_id         varchar(4),
president_batch             int,
vice_president_roll_no      varchar(11),
vice_president_branch_id    varchar(4),
vice_president_batch        int,
faculty_mentor              varchar(50),
topic                       varchar(50) not null,
constraint c_pk primary key(c_id,c_year),
constraint p_fk foreign key(president_roll_no, president_branch_id, president_batch) references student(roll_no, branch_id, batch),
constraint vp_fk foreign key(vice_president_roll_no, vice_president_branch_id, vice_president_batch) references student(roll_no, branch_id, batch)
);
exec sp_columns club;

create table uevent(
    event_id                    varchar(10),
    event_start_date            date,
    event_end_date              date,
    event_logo_url              varchar(50),
    event_location              varchar(50),
    isOnline                    boolean,
    organizing_head_roll_no     varchar(11),
    organizing_head_branch_id   varchar(4),
    organizing_head_batch       int,
    constraint e_pk primary key(e_id),
    constraint oh_fk foreign key(organizing_head_roll_no, organizing_head_branch_id, organizing_head_batch) references student(roll_no, branch_id, batch)
);
exec sp_columns uevent;

create table eSessions(
    event_id    varchar(10),
    session_id  varchar(10),
    session_name varchar(20),
    constraint s_fk foreign key(event_id) references uevent,
    constraint s_pk primary key(event_id, session_id)
);
exec sp_columns eSessions;

create table eCoreTeam(
    event_id            varchar(10),
    member_roll_no     varchar(11),
    member_branch_id   varchar(4),
    member_batch       int,
    constraint ct_fk foreign key(event_id) references uevent,
    constraint ctm_fk foreign key(member_roll_no, member_branch_id, member_batch) references student(roll_no, branch_id, batch),
    constraint ct_pk primary key(event_id, member_roll_no, member_branch_id, member_batch)
);
exec sp_columns eCoreTeam;

create table subEvent(
    event_id                    varchar(10),
    subEvent_id                 varchar(10),
    subEvent_name               varchar(30),
    subEvent_logo_url           varchar(50),
    subEvent_location           varchar(50),
    isOnline                    boolean,
    corecoordinator_roll_no     varchar(11),
    corecoordinator_branch_id   varchar(4),
    corecoordinator_batch       int,
    coordinator_roll_no         varchar(11),
    coordinator_branch_id       varchar(4),
    coordinator_batch           int,
    constraint se_fk foreign key(event_id) references uevent,
    constraint se_pk primary key(event_id, subEvent_id),
    constraint secc_fk foreign key(corecoordinator_roll_no, corecoordinator_branch_id, corecoordinator_batch) references student(roll_no, branch_id, batch),
    constraint sec_fk foreign key(coordinator_roll_no, coordinator_branch_id, coordinator_batch) references student(roll_no, branch_id, batch)
);
exec sp_columns subEvent;