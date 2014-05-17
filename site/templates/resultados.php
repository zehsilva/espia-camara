<!DOCTYPE html>
<html>
  <head>
    <title>Deputado Mining - Resultado da busca</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">

    <!-- HTML5 Shim and Respond.js IE8 support of HTML5 elements and media queries -->
    <!-- WARNING: Respond.js doesn't work if you view the page via file:// -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <?php include('navbar.php'); ?>
    <div class="jumbotron">
      <div class="container">
        <h2>Resultados da sua busca</h2>
        <p>Você buscou por "<i><?php echo $query?></i>".</p>
      </div>
    </div>
    <div class="container">
      <?php if (sizeof($resultados) > 0){
        foreach ($resultados as $deputado) {?>
          <div class="row panel panel-default">
            <div class="col-md-2">
              <a href="/deputado/<?php echo $deputado['id_deputado']?>">
                <?php if (strlen ($deputado['url_foto'])>0){?><img src="<?php echo $deputado['url_foto'];?>" alt="Deputado"><?php }
                 else {?>
                 <div class="panel">Deputado sem foto</div>
                <?php }?>
              </a>
              <a class="btn btn-primary btn-sm" role="button" href="/deputado/<?php echo $deputado['id_deputado']?>">Mais detalhes</a>
            </div>
            <div class="col-md-3">
              <h3><?php echo $deputado['nome_parlamentar'];?></h3>
              <dl class="dl-horizontal">
                <dt>Eleito pelo estado:</dt>
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
          <div class="alert alert-danger">Não encontramos nenhum deputado com esse termo. Por que você não procura por outro termo na caixinha ali em cima?</div>
        <?php } ?>
    </div>
    <script src="https://code.jquery.com/jquery.js"></script>
    <?php include('footer.php'); ?>
  </body>
</html>
