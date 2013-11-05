<?php
require 'Slim/Slim.php';
require 'Slim/View.php';
require '/bdCon.php';

\Slim\Slim::registerAutoloader();
$app = new \Slim\Slim(array(
    //'view' => new Twig(),
    'mode' => 'development',
));

// Configura o modo de produção
$app->configureMode('production', function () use ($app) {
    $app->config(array(
        'log.enable' => true,
        'debug' => false
    ));
});

// Configura o modo de desenvolvimento
$app->configureMode('development', function () use ($app) {
    $app->config(array(
        'log.enable' => true,
        'debug' => true
    ));
});

/**
 * Rotas de páginas
 */

// Páginas Fixas
$app->get('/', function () use($app) {$app->render('home.php');});
$app->get('/sobre', function () use($app) {$app->render('sobre.php');});
$app->get('/contato', function () use($app) {$app->render('contato.php');});

//Página dinâmicas
$app->get('/deputado/:id', function ($id) use($app) {
        $d = getDeputado($id);
        $app->view->setData('id', $id);
        $app->view->setData('nome_parlamentar', $d->nome_parlamentar);
        $app->view->setData('uf', $d->uf);
        $app->view->setData('eleicao_partido', $d->eleicao_partido);
        $app->view->setData('partido_atual', $d->partido_atual);
        $app->view->setData('url_foto', $d->url_foto);
        $app->view->setData('nome_completo', $d->nome_completo);
        $app->view->setData('data_nascimento', $d->data_nascimento);
        $app->view->setData('nome_profissao', $d->nome_profissao);
        $app->view->setData('titulo_eleitoral', $d->titulo_eleitoral);
        $app->view->setData('cpf', $d->cpf);
        $app->view->setData('sexo', $d->sexo);
        $app->view->setData('email', $d->email);
        $app->view->setData('gabinete', $d->gabinete);
        $app->view->setData('url_facebook', $d->url_facebook);
        $app->view->setData('url_twitter', $d->url_twitter);

        $l = getLegislaturasDeputado($id);
        $app->view->setData('mandatos', $l);

        $trocas = getTrocasPartidoDeputado($id);
        $app->view->setData('trocas', $trocas);
        $app->render('deputado.php');
    }
);

$app->get('/topicos', function () use($app) {
        $d = getTopicosHome();
        $app->view->setData('dados', $d);
        $app->render('topicos.php');
    }
);

$app->post('/resultados', function () use($app) {
        $parametros = $app->request()->params();
        $query = $parametros['query'];
        $app->view->setData('resultados', getDeputadosPorNome($query));
        $app->view->setData('query', $query);
        $app->render('resultados.php');
    }
);


/**
 * Rotas para requisições AJAX
  */
$app->get('/getTopicosProposicoesDeputado/:id', 'getTopicosProposicoesDeputado'); //topicos de um deputado
$app->get('/getTopicosDiscursosDeputado/:id', 'getTopicosDiscursosDeputado'); //topicos de um deputado
$app->get('/getVotosDeputado/:id', 'getVotosDeputado'); //votos que um deputado recebeu na sua última eleição
$app->get('/getPresencasDeputado/:id', 'getPresencasDeputado'); //presenças do deputado


$app->run();

function getDeputado($id){
    $sql = "SELECT dep.nome_parlamentar, dep.uf,
                dep.eleicao_partido, dep.partido_atual,
                dep.url_foto, dep.nome_completo,
                dep.data_nascimento, prof.nome_profissao,
                dep.titulo_eleitoral, dep.cpf,
                dep.sexo, dep.email, dep.gabinete,
                dep.url_facebook, dep.url_twitter
            FROM deputados AS dep,
                profissoes AS prof
            WHERE dep.id_deputado = :id AND
                prof.id_profissao = dep.profissao";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $deputado = $stmt->fetchObject();
    $db = null;
    return $deputado;
}
function getLegislaturasDeputado($id){
    $sql = "SELECT dl.ano_inicio
            FROM deputados_legislaturas AS dl
            WHERE dl.id_deputado = :id
            ORDER BY dl.ano_inicio DESC";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $deputado = $stmt->fetchAll();
    $db = null;
    return $deputado;
}
function getTrocasPartidoDeputado($id){
    $sql = "SELECT p.nome_partido,
                DATE_FORMAT(dp.data_saida, '%d/%m/%Y')
            FROM partidos as p,
                deputados_partidos as dp
            WHERE dp.id_partido = p.id_partido AND
                dp.id_deputado = :id";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $res = $stmt->fetchAll();
    $db = null;
    return $res;
}
function getTopicosHome(){
    $sql = "SELECT tp.id_topico, tp.peso,
                GROUP_CONCAT(tpl.palavra) as palavra
            FROM ml_topicos as tp, ml_topicos_palavras as tpl
            WHERE tpl.id_topico = tp.id_topico
            GROUP BY tp.id_topico";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $deputado = $stmt->fetchAll();
    $db = null;
    return $deputado;
}
function getTopicosProposicoesDeputado($id){
    $sql = "SELECT TP.palavra, TP.peso, T.id_topico
            FROM ml_topicos_palavras AS TP,
                ml_topicos AS T,
                ml_proposicoes_topicos AS PT,
                proposicoes AS P,
                autores_proposicoes AS AP
            WHERE T.id_topico = TP.id_topico and
                PT.id_topico = T.id_topico and
                P.id_proposicao = PT.id_proposicao and
                AP.id_autor = P.autor1 and
                AP.id_deputado = :id";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $topicos = $stmt->fetchAll();
    $db = null;
    echo json_encode($topicos);
}
function getTopicosDiscursosDeputado($id){
    $sql = "SELECT TP.palavra, TP.peso, T.id_topico
            FROM ml_topicos_palavras AS TP,
                ml_topicos AS T,
                ml_discursos_topicos AS DT,
                discursos AS D
            WHERE T.id_topico = TP.id_topico and
                DT.id_topico = T.id_topico and
                D.id_discurso = DT.id_discurso and
                D.id_deputado = :id";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $topicos = $stmt->fetchAll();
    $db = null;
    echo json_encode($topicos);
}
function getVotosDeputado($id){
    $sql = "SELECT m.latitude, m.longitude, dev.votos
            FROM deputados_eleicoes_votacoes dev,
                municipios m
            WHERE dev.id_municipio = m.id_municipio and
            dev.id_deputado = :id";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $votos = $stmt->fetchAll();
    $db = null;
    echo json_encode($votos);
}
function getPresencasDeputado($id){
    $sql = "SELECT dsp.data_reuniao, dsp.presenca
            FROM deputados_sessoes_presencas as dsp
            WHERE id_deputado = :id";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("id", $id);
    $stmt->execute();
    $presencas = $stmt->fetchAll();
    $db = null;
    echo json_encode($presencas);
}
function getDeputadosPorNome($query){
    $sql = "SELECT dep.id_deputado, dep.nome_parlamentar, dep.uf,
                dep.partido_atual, dep.url_foto,
                dep.titulo_eleitoral, dep.cpf,
                dep.email
            FROM deputados AS dep
            WHERE dep.nome_parlamentar like concat('%', :query, '%') OR
                dep.nome_completo like concat('%', :query, '%')";
    $db = getConnection();
    $stmt = $db->prepare($sql);
    $stmt->bindParam("query", $query, PDO::PARAM_STR);
    $stmt->execute();
    $resultados = $stmt->fetchAll();
    $db = null;
    return $resultados;
}
