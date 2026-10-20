# Restrições de exploração do simple_system; não representam a interface final.
# O SDC da imagem cria clock, delays máximos, cargas e driving cells do PDK.
source $::env(SCRIPTS_DIR)/base.sdc

# Reset é síncrono: continua sendo uma entrada temporizada, sem false path.
# Atrasos máximos vêm de IO_DELAY_CONSTRAINT (20% do período); mínimos em ns.
set_input_delay -clock [get_clocks clk_i] -min 0.5 [get_ports rst_i]
set_output_delay -clock [get_clocks clk_i] -min 0.5 \
    [get_ports {done_o success_o fault_o}]

# A FSM é multiciclo, mas a lógica entre registradores deve fechar a cada ciclo.
# Não declaramos multicycle paths para relaxar indiscriminadamente o datapath.
