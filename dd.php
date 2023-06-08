global $wpdb;
$idposts = get_the_ID();
$the_title = get_the_title( $post = $idposts );
//update_post_meta($idpozsts, "value_idpost", $idposts);
if ($wpdb) {
$resultCC = $wpdb->get_results("SELECT wpnj_e_submissions_values.id AS Value_id, 
       MAX(CASE WHEN wpnj_e_submissions_values.key = 'ufa_id' THEN value ELSE 0 end) as `ufa_user`,
       MAX(CASE WHEN wpnj_e_submissions_values.key = 'score_input' THEN value ELSE 0 end) as `score`,
       MAX(CASE WHEN wpnj_e_submissions_values.key  = 'field_home_score' THEN value ELSE 0 end) as `field_home_score`,
       MAX(CASE WHEN wpnj_e_submissions_values.key  = 'field_away_score' THEN value ELSE 0 end) as `field_away_score`,
       MAX(CASE WHEN wpnj_e_submissions_values.key  = 'date_time' THEN value ELSE 0 end) as `field_ffrom_pr`,
       SUBSTRING_INDEX(MAX(CASE WHEN wpnj_e_submissions_values.key = 'score_input' THEN value ELSE 0 end) , '-', 1) AS `score_pr_home`,
       SUBSTRING_INDEX(MAX(CASE WHEN wpnj_e_submissions_values.key = 'score_input' THEN value ELSE 0 end) , '-', -1) AS `score_pr_away`,
       wpnj_e_submissions.form_name,
       wpnj_e_submissions.user_ip,
       wpnj_e_submissions.user_id,
       wpnj_e_submissions.hash_id
FROM wpnj_e_submissions  
LEFT JOIN wpnj_e_submissions_values ON wpnj_e_submissions_values.submission_id = wpnj_e_submissions.id
WHERE wpnj_e_submissions.form_name = '".$idposts."'
GROUP BY main_meta_id  
ORDER BY wpnj_e_submissions.main_meta_id DESC");
{?>
<h3 class="title_ta"><?= $the_title; ?></h3>
<?php }
if (empty($resultCC)) {return;}
{?>
<div><table id="table_user" class="table"><thead><tr><th>วันเวลา
</th><th>USER ID</th><th>ทายผล</th></tr></thead><tbody>
<?php }
foreach ($resultCC as $result) {
//$Score_IDX = explode("-", $result->score);
update_post_meta($idposts, "value_AllSXZ", json_encode($result));
update_post_meta($idposts, "value_pr_home_count", $result->score_pr_home);
update_post_meta($idposts, "value_pr_away_count", $result->score_pr_away);
{?><tr>
<td><?= $result->field_ffrom_pr; ?></td>
<td id="userID"><?= $result->ufa_user; ?></td>
<td><?= $result->score; ?></td>
<!--<td id="team_slect"><?php }if($Score_IDX[0] > $Score_IDX[1]){$Score_W = "HOME";}else if($Score_IDX[0] < $Score_IDX[1]){$Score_W = "AWAY";}else{$Score_W = "DRAW";}print_r($Score_W);{?>
</td>-->
</tr><?php }
}
{?></tbody></table></div><?php }
}