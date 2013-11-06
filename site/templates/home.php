<!DOCTYPE html>
<html>
  <head>
    <title>Espia C�mara - P�gina Inicial</title>
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
        <h2>Espia C�mara</h2>
        <p>Se voc� sempre quis espiar o que anda acontecendo na c�mara dos deputados, essa � sua chance!
          O Espia C�mara � um site que est� de olho na atua��o parlamentar de uma forma que nem os deputados est�o!
        </p>
        <p>N�s utilizamos t�cnicas de intelig�ncia artificial (<i>minera��o de dados</i>) para detectar padr�es nos dados abertos da c�mara.
          Se voc� prestar aten��o, abaixo tem uma nuvem de t�picos. Esses s�o os t�picos extra�dos automaticamente de todas as proposi��es e discursos.</p>
        <p>Para come�ar, por que voc� n�o clica num desses t�picos para ver que deputados est�o se preocupando com isso?
          Voc� tamb�m pode pesquisar por um deputado na caixa ali em cima e ver o perfil que preparamos.</p>
        <p><a class="btn btn-primary btn-lg" role="button" href="/sobre">Para mais detalhes, acesse a p�gina Sobre &raquo;</a></p>
      </div>
    </div>

    <div class="container" style="padding-top: 50px;">
      TOPICOS
    </div>

    <?php include('footer.php');?>
  </body>
</html>
