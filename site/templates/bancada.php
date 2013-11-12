<!DOCTYPE html>
<html>
  <head>
    <title>Deputado Mining - Bancada <?php echo $id+1?> - Deputados e Proposi��es</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">
    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <?php include 'navbar.php';?>
    <div class="jumbotron">
      <div class="container">
        <h2>Bancada <?php echo $id+1?></h2>
        <p>Essa bancada foi descoberta utilizando t�cnicas de intelig�ncia artificial. Os deputados abaixo votaram de forma muito semelhante nas proposi��es descritas.</p>
        <a class="btn btn-primary btn-lg" role="button" href="/sobre/biclusterizacao">Saiba mais sobre como descobrimos as bancadas &raquo;</a>
      </div>
    </div>
    <div class="container">
      <div class="row">
        <div class="col-md-6">
          <h3>Deputados participantes</h3>
          <?php if (sizeof($deputados) > 0){
            foreach ($deputados as $deputado) {?>
              <div class="row panel panel-default">
                <div class="col-md-3">
                  <a href="/deputado/<?php echo $deputado['id_deputado']?>">
                    <?php if (strlen ($deputado['url_foto'])>0){?><img src="<?php echo $deputado['url_foto'];?>" alt="Deputado"><?php }
                     else {?>
                     <div class="panel">Deputado sem foto</div>
                    <?php }?>
                  </a>
                  <a class="btn btn-primary btn-sm" role="button" href="/deputado/<?php echo $deputado['id_deputado']?>">Mais detalhes</a>
                </div>
                <div class="col-md-6">
                  <h3><?php echo $deputado['nome_parlamentar'];?></h3>
                  <dl>
                    <dt>Estado:</dt>
                    <dd><?php echo $deputado['uf'];?></dd>
                    <dt>Partido atual:</dt>
                    <dd><?php echo $deputado['partido_atual'];?></dd>
                    <dt>E-mail:</dt>
                    <dd><?php echo $deputado['email'];?></dd>
                  </dl>
                </div>
              </div>
            <?php }
            } else {?>
              <div class="alert alert-danger">Essa bancada n�o cont�m deputados. Podemos concluir que nenhum deputado votou semelhante para as proposi��es ao lado.</div>
            <?php } ?>
        </div>
        <div class="col-md-6">
          <h3>Proposi��es em que votaram parecido</h3>
          <?php if (sizeof($proposicoes) > 0){?>
             <table class="table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Link para o conte�do</th>
                  <th>t�pico</th>
                </tr>
              </thead>
              <tbody>
                <?php $i = 1;
                foreach ($proposicoes as $proposicao) {?>
                  <tr>
                    <td><?php echo $i ?></td>
                    <td><a href="<?php echo $proposicao['link_conteudo'] ?>" target="_blank">Conte�do da proposi��o</a></td>
                    <td><?php echo $proposicao['topicos'] ?></td>
                  </tr>
                  <?php $i = $i+1;
                 }?>
              </tbody>
            </table>
          <?php } else {?>
            <div class="alert alert-danger">Essa bancada n�o cont�m proposi��es. Podemos concluir que os deputados ao lado n�o votaram de forma semelhante em nenhuma proposi��o.</div>
          <?php } ?>
        </div>
      <div>
    </div>
    <script src="https://code.jquery.com/jquery.js"></script>
    <?php include('footer.php');?>
  </body>
</html>
