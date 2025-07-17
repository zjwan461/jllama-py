alter table sd_info
    add column ip_adapter_state varchar(50) default '待初始化';

alter table sd_info
    add column ip_adapter_faceid_state varchar(50) default '待初始化';

alter table sd_info
    add column ip_adapter_model_path varchar(500);

alter table sd_info
    add column insightface_model_path varchar(500);

alter table sd_info
    add column image_encoder_model_path varchar(500);

alter table sd_info
    add column ip_adapter_faceid_model_path varchar(500);