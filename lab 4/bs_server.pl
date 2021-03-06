use lib "/home/negarr/Desktop/Net-Centric/lab 4";
use Field;
use IO::Socket;
use Time::HiRes qw(usleep);

$| = 1;

$socket = new IO::Socket::INET (
	LocalHost => '127.0.0.1',
	LocalPort => '9998',
	Proto => 'tcp',
	Listen => 2,
	Reuse => 1
) or die "Coudn't open socket\n";

print "TCPServer Waiting for client on port 9998\n";


while(1){

	$p1_socket = $socket->accept();
	print "A player has joined the game. Waiting for 1 more player\n";
	$p1_socket->send("You are player 1. Please wait for another player to join the game\n");
	
	$p2_socket = $socket->accept();
	print "Two players joined. The game is starting.\n";
	$p2_socket->send("You are player 2. The game is starting\n");
	$p1_socket->send("Player 2 joined the game. The game is starting\n");
	
	$cur_player = int(rand(10)) > 4 ? 1 : 2;
	
	$field = Field->new();
	
	while (1) {
		if ($cur_player == 1){
			foreach ($field->viewall()){
				print join ', ', @$_;
				print $/;
			}
			$p1_socket->send("It is your turn\n");
			foreach ($field->view(1)){
				usleep(100);
				$p1_socket->send(join ', ', @$_);
				usleep(100);
				$p1_socket->send("\n");
			}
			usleep(100);
			$p1_socket->send("You can move one of your ships by entering the ship you want to move and the destination\n");
			usleep(100);
			$p1_socket->send("mv");
			$p1_socket->recv($cmd, 1024);
			usleep(100);
			$p1_socket->send($field->move($cur_player, $cmd));
			usleep(100);
			$p1_socket->send("\n");
			foreach ($field->view(1)){
				usleep(100);
				$p1_socket->send(join ', ', @$_);
				usleep(100);
				$p1_socket->send("\n");
			}
			usleep(100);
			$p1_socket->send("You can shoot using one of your ships by entering the ship you want to shoot and the target\n");
			usleep(100);
			$p1_socket->send("sh");
			$p1_socket->recv($cmd, 1024);
			usleep(100);
			$p1_socket->send($field->shoot($cur_player, $cmd));
			usleep(100);
			$p1_socket->send("\nTurn ended, please wait for your next turn\n");
		} else {
			foreach ($field->viewall()){
				print join ', ', @$_;
				print $/;
			}
			$p2_socket->send("It is your turn\n");
			foreach ($field->view(2)){
				usleep(100);
				$p2_socket->send(join ', ', @$_);
				usleep(100);
				$p2_socket->send("\n");
			}
			usleep(100);
			$p2_socket->send("You can move one of your ships by entering the ship you want to move and the destination\n");
			usleep(100);
			$p2_socket->send("mv");
			$p2_socket->recv($cmd, 1024);
			usleep(100);
			$p2_socket->send($field->move($cur_player, $cmd));
			usleep(100);
			$p2_socket->send("\n");
			foreach ($field->view(2)){
				usleep(100);
				$p2_socket->send(join ', ', @$_);
				usleep(100);
				$p2_socket->send("\n");
			}
			usleep(100);
			$p2_socket->send("You can shoot using one of your ships by entering the ship you want to shoot and the target\n");
			usleep(100);
			$p2_socket->send("sh");
			$p2_socket->recv($cmd, 1024);
			usleep(100);
			$p2_socket->send($field->shoot($cur_player, $cmd));
			usleep(100);
			$p2_socket->send("\nTurn ended, please wait for your next turn\n");
		}
		$cur_player = $cur_player == 1 ? 2 : 1;
		if ($field->ended()){
			$p1_socket->send($field->ended);
			$p2_socket->send($field->ended);
			close $p1_socket;
			close $p2_socket;
			last;
		}
	}
}
