with hard_drive_data as (
    select * from {{ ref("stg_hard_drive_data")}}
)
, grp_datacenter_info as (
select datacenter, cluster_id, vault_id, pod_id, pod_slot_num
from hard_drive_data
group by datacenter, cluster_id, vault_id, pod_id, pod_slot_num
)
select count(distinct datacenter) as dcs
, count(distinct cluster_id) as clusters
, count(distinct vault_id) as vaults
, count(distinct pod_id) as pods
, count(distinct pod_slot_num) as pod_slots
from grp_datacenter_info