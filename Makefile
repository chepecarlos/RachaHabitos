
install:
	@echo "Instalando paquete..."
	pipx install . --force


service:
	@echo "Preparando servicio..."
	sudo cp RachaHabito.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable RachaHabito.service
	sudo systemctl start RachaHabito.service
