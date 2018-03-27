use IO::Socket;
use List::Util 'shuffle';

$| = 1;

$socket = new IO::Socket::INET (
	LocalHost => '127.0.0.1',
	LocalPort => '9999',
	Proto => 'tcp',
	Listen => 5,
	Reuse => 1
) or die "Coudn't open socket\n";

print "TCPServer Waiting for client on port 9999\n";

while(1){

	$client_socket = "";
	$client_socket = $socket->accept();
	
	$peer_address = $client_socket->peerhost();
	$peer_port = $client_socket->peerport();
	
	print "Connection from ($peer_address, $peer_port)\n";
	
	$client_socket->recv($cmd, 1024);
	lc $cmd;
	while (1) {	
		if ($cmd eq "spin"){
			my @num = (shuffle 1 .. 45)[0..5];
			my $data = join(' ', @num);
			$client_socket->send("$data\n");
		}
		elsif ($cmd eq "exit"){
			$client_socket->send("exit");
			close $client_socket;
			last;
		}
		$client_socket->recv($cmd, 1024);
		lc $cmd;
	}
	last;
	
}
