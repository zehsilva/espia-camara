EXEC=1
mkdir exec_atual
while true
	do
	echo "Execução $EXEC"
	if [ $EXEC == 1 ]
		then
		./obtem_dados.py > saidas.log 2> erros.log
	else
		./obtem_dados.py -r > saidas.log 2> erros.log
	fi
	if [ $? == 0 ]
		then
		break
	fi
	mkdir exec_atual/$EXEC
	mv saidas.log erros.log exec_atual/$EXEC
	cp -r *.part exec_atual/$EXEC
	EXEC=$(expr $EXEC + 1)
done
mkdir exec_atual/final
cp -r saidas.log erros.log *.part exec_atual/final

