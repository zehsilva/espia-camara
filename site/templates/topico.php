<!DOCTYPE html>
<html>
  <head>
    <title>Deputado Mining - Tópico</title>
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
    <?php include('navbar.php'); ?>
    <div class="jumbotron">
      <div class="container">
        <h2>Tópico de interesse</h2>
        <p>Esse tópico é descrito por cinco palavras:</p>
        <p class="text-info">
          <?php $texto = array();
            foreach ($palavras as $palavra) {
              $texto[] = $palavra['palavra'];
            }
            $result = implode(", ",$texto); echo $result;
          ?>.
        </p>
      </div>
    </div>
    <div class="container">
      <div class="row">
        <div class="col-sm-6">
          <div class="panel panel-default">
            <div class="panel-heading">
              <p>Esses são os 10 deputados autores das 10 proposições mais relevantes para esse tópico:</p>
            </div>
            <div class="panel-body">
              <?php if (sizeof($deputadosProp) > 0){
                foreach ($deputadosProp as $deputado) {?>
                  <div class="row panel panel-default">
                    <div class="col-md-4">
                      <a href="/deputado/<?php echo $deputado['id_deputado']?>">
                        <?php if (strlen ($deputado['url_foto'])>0){?><img src="<?php echo $deputado['url_foto'];?>" alt="Deputado"><?php }
                         else {?>
                         <div class="panel">Deputado sem foto</div>
                        <?php }?>
                      </a>
                      <a class="btn btn-primary btn-sm" role="button" href="/deputado/<?php echo $deputado['id_deputado']?>">Ver Perfil</a>
                    </div>
                    <div class="col-sm-8">
                      <h3><?php echo $deputado['nome_parlamentar'];?></h3>
                      <dl>
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
                  <div class="alert alert-danger">Parece que nenhum deputado faz proposições relacionadas a esse tópico. :-/</div>
                <?php } ?>
            </div>
          </div>
        </div>
        <div class="col-sm-6">
          <div class="panel panel-default">
            <div class="panel-heading">
              <p>Esses são os 10 deputados com os 10 discursos mais relevantes para esse tópico</p>
            </div>
            <div class="panel-body">
              <?php if (sizeof($deputadosDisc) > 0){
                foreach ($deputadosDisc as $deputado) {?>
                  <div class="row panel panel-default">
                    <div class="col-md-4">
                      <a href="/deputado/<?php echo $deputado['id_deputado']?>">
                        <?php if (strlen ($deputado['url_foto'])>0){?><img src="<?php echo $deputado['url_foto'];?>" alt="Deputado"><?php }
                         else {?>
                         <div class="panel">Deputado sem foto</div>
                        <?php }?>
                      </a>
                      <a class="btn btn-primary btn-sm" role="button" href="/deputado/<?php echo $deputado['id_deputado']?>">Ver Perfil</a>
                    </div>
                    <div class="col-md-8">
                      <h3><?php echo $deputado['nome_parlamentar'];?></h3>
                      <dl>
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
                  <div class="alert alert-danger">Parece que nenhum deputado discursa sobre esse tópico. :-/</div>
                <?php } ?>
            </div>
          </div>
        </div>
      </div>
    </div>
    <script src="https://code.jquery.com/jquery.js"></script>
    <?php include('footer.php'); ?>
  </body>
</html>
