<?php
$lines = array();
while (!feof(STDIN)) {
    $line = fgets(STDIN);
    if ($line === false) break;
    $lines[] = $line;
}
$data = implode('', $lines);
$tokens = token_get_all($data);
$line_num = 0;
foreach ($tokens as $token) {
    if (isset($token[2])) $line_num = $token[2];
    if (isset($token[1])) {
        $token_name = token_name($token[0]);
        $token_value = $token[1];
    } else {
        $token_name = 'T_OP';
        $token_value = $token[0];
    }
    // if ($token_name == 'T_WHITESPACE') continue;
    printf("(%s,%s,%d)\n",
           preg_replace('/^T_/', '', $token_name),
           str_replace('\/', '/', json_encode($token_value)),
           $line_num);
}
