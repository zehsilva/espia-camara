<?php

require 'Slim/Slim.php';
Slim::registerAutoloader();

$app = new Slim(array(
    'debug' => true,
    'log.level' => \Slim\Log::DEBUG,
    'log.enabled' => true
));

$app->get('/deputado', 'getDeputado');

$app->run();

function getDeputado() {
		echo 'teste';
}
 
?>