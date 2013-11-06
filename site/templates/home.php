<!DOCTYPE html>
<html>
  <head>
    <title>Espia Câmara - Página Inicial</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Bootstrap -->
    <link href="http://netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet" media="screen">

    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
      <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <?php include 'navbar.php';?>

    <div class="jumbotron">
      <div class="container">
        <h2>Espia Câmara</h2>
        <p>Se você sempre quis espiar o que anda acontecendo na câmara dos deputados, essa é sua chance!
          O Espia Câmara é um site que está de olho na atuação parlamentar de uma forma que nem os deputados estão!
        </p>
        <p>Nós utilizamos técnicas de inteligência artificial (<i>mineração de dados</i>) para detectar padrões nos dados abertos da câmara.
          Se você prestar atenção, abaixo tem uma nuvem de tópicos. Esses são os tópicos extraídos automaticamente de todas as proposições e discursos.</p>
        <p>Para começar, por que você não clica num desses tópicos para ver que deputados estão se preocupando com isso?
          Você também pode pesquisar por um deputado na caixa ali em cima e ver o perfil que preparamos.</p>
        <p><a class="btn btn-primary btn-lg" role="button" href="/sobre">Para mais detalhes, acesse a página Sobre &raquo;</a></p>
      </div>
    </div>

    <div class="container" style="padding-top: 50px;">
      TOPICOS
    </div>

    <?php include('footer.php');?>
  </body>
</html>
