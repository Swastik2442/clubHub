create table branch(
    branch_id   varchar(4),
    branch_name varchar(30),
    constraint b_pk primary key (branch_id)
);
exec sp_columns branch;

create table student(
    roll_no     int,
    s_name      varchar(50),
    branch_id   varchar(4),
    batch       int,
    constraint s_pk primary key(roll_no,branch_id,batch),
    constraint b_fk foreign key(branch_id) references branch
);
exec sp_columns student;

create table club(
    club_id                     varchar(10) not null,
    club_name                   varchar(50) not null,
    club_year                   int not null,
    club_logo_url               varchar(200),
    president_roll_no           varchar(11),
    president_branch_id         varchar(4),
    president_batch             int,
    president_picture_url       varchar(200),
    vice_president_roll_no      varchar(11),
    vice_president_branch_id    varchar(4),
    vice_president_batch        int,
    vice_president_picture_url  varchar(200),
    faculty_mentor              varchar(50),
    faculty_mentor_picture_url  varchar(200),
    topic                       varchar(50) not null,
    constraint c_pk primary key(c_id,c_year),
    constraint p_fk foreign key(president_roll_no, president_branch_id, president_batch) references student(roll_no, branch_id, batch),
    constraint vp_fk foreign key(vice_president_roll_no, vice_president_branch_id, vice_president_batch) references student(roll_no, branch_id, batch)
);
exec sp_columns club;

create table clubMember(
    club_id             varchar(10) not null,
    club_year           int not null,
    member_roll_no      int not null,
    member_branch_id    varchar(4) not null,
    member_batch        int not null,
    member_role         varchar(20) not null,
    constraint cmc_fk(club_id, club_year) references club(club_id, club_name),
    constraint cmm_fk(member_roll_no, member_branch_id, member_batch) references student(roll_no, branch_id, member_batch),
    constraint cm_pk(club_id, club_year, member_roll_no, member_branch_id, member_batch)
);

create table uevent(
    event_id                    varchar(10) not null,
    event_name                  varchar(30) not null,
    event_start_date            date not null,
    event_end_date              date,
    event_logo_url              varchar(200),
    event_location              varchar(50),
    isOnline                    boolean,
    organizing_head_roll_no     varchar(11),
    organizing_head_branch_id   varchar(4),
    organizing_head_batch       int,
    repetition                  varchar(10),
    constraint e_pk primary key(event_id),
    constraint oh_fk foreign key(organizing_head_roll_no, organizing_head_branch_id, organizing_head_batch) references student(roll_no, branch_id, batch)
);
exec sp_columns uevent;

create table eSessions(
    event_id            varchar(10) not null,
    session_id          varchar(10) not null,
    session_name        varchar(20),
    session_start_date  date not null,
    session_end_date    date,
    constraint s_fk foreign key(event_id) references uevent,
    constraint s_pk primary key(event_id, session_id)
);
exec sp_columns eSessions;

create table eCoreTeam(
    event_id         varchar(10) not null,
    member_roll_no   varchar(11) not null,
    member_branch_id varchar(4) not null,
    member_batch     int not null,
    constraint ct_fk foreign key(event_id) references uevent,
    constraint ctm_fk foreign key(member_roll_no, member_branch_id, member_batch) references student(roll_no, branch_id, batch),
    constraint ct_pk primary key(event_id, member_roll_no, member_branch_id, member_batch)
);
exec sp_columns eCoreTeam;

create table eOperationsTeam(
    event_id                    varchar(10) not null,
    team_id                     varchar(10) not null,
    team_name                   varchar(20) not null,
    coreCoordinator_roll_no     varchar(11),
    coreCoordinator_branch_id   varchar(4),
    coreCoordinator_batch       int,
    relatedClub_id              varchar(10),
    relatedClub_year            int,
    constraint ote_fk foreign key(event_id) references uevent,
    constraint otcc_fk foreign key(coreCoordinator_roll_no, coreCoordinator_branch_id, coreCoordinator_batch) references student(roll_no, branch_id, batch),
    constraint otc_fk foreign key(relatedClub_id, relatedClub_year) references club(club_id, club_year),
    constraint ot_pk primary key(event_id, team_id)
);
exec sp_columns eOperationsTeam;

create table subEvent(
    event_id                    varchar(10) not null,
    subEvent_id                 varchar(10) not null,
    subEvent_name               varchar(30) not null,
    subEvent_logo_url           varchar(200),
    subEvent_location           varchar(50),
    isOnline                    boolean,
    coreCoordinator_roll_no     varchar(11),
    coreCoordinator_branch_id   varchar(4),
    coreCoordinator_batch       int,
    coordinator_roll_no         varchar(11),
    coordinator_branch_id       varchar(4),
    coordinator_batch           int,
    constraint se_fk foreign key(event_id) references uevent,
    constraint se_pk primary key(event_id, subEvent_id),
    constraint secc_fk foreign key(coreCoordinator_roll_no, coreCoordinator_branch_id, coreCoordinator_batch) references student(roll_no, branch_id, batch),
    constraint sec_fk foreign key(coordinator_roll_no, coordinator_branch_id, coordinator_batch) references student(roll_no, branch_id, batch)
);
exec sp_columns subEvent;