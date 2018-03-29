package Field;

use lib "/home/negarr/Desktop/net centric/lab 4";
use Ship;

my $p1_s1 = Ship->new(hp=>200,dmg=>50,owner=>1);
my $p1_s2 = Ship->new(hp=>100,dmg=>75,owner=>1);
my $p1_s3 = Ship->new(hp=>100,dmg=>50,owner=>1);
my $p1_s4 = Ship->new(hp=>100,dmg=>50,owner=>1);
my $p1_s5 = Ship->new(hp=>100,dmg=>50,owner=>1);
my $p2_s1 = Ship->new(hp=>200,dmg=>50,owner=>2);
my $p2_s2 = Ship->new(hp=>100,dmg=>75,owner=>2);
my $p2_s3 = Ship->new(hp=>100,dmg=>50,owner=>2);
my $p2_s4 = Ship->new(hp=>100,dmg=>50,owner=>2);
my $p2_s5 = Ship->new(hp=>100,dmg=>50,owner=>2);


sub shuffleRefs (\@) {
    my $r=pop;
    $a = $_ + rand @{$r} - $_
    and (${$r->[$_]}, ${$r->[$a]}) = (${$r->[$a]}, ${$r->[$_]})
    for (0..$#{$r});
}

sub shuffle2d {
    my @refs;
    push @refs, \( @$_ ) for @_;
    shuffleRefs @refs;
    return @refs;
}

my @array = (
		[$p1_s1,$p1_s2,$p1_s3,$p1_s4,$p1_s5],
		[$p2_s1,$p2_s2,$p2_s3,$p2_s4,$p2_s5],
		[(undef) x 5],
		[(undef) x 5],
		[(undef) x 5],
		);
		
shuffle2d @array;

sub new {
	my $class = shift;
	my $self = {@_};
	bless ($self, $class);
	
	return $self;
}

sub viewall {
	my $self = shift;
	my @view;
	foreach (@array){
		my @temp = map {defined $_ ? $_->owner() : 0} @$_;
		push @view, \@temp;
	}
	return @view;
}

sub view {
	my $self = shift;
	my $player = @_[0];
	my @view;
	foreach (@array){
		my @temp = map {defined $_ ? ($_->owner() == $player and $_->alive() > 0) ? $_->owner() : 0 : 0} @$_;
		push @view, \@temp;
	}
	return @view;
}

sub shoot {
	my $self = shift;
	my $cur_player = shift;
	my $piece = (split /\W+/, @_[0])[0];
	my $target = (split /\W+/, @_[0])[1];
	my $piece_x = (split //, $piece)[0] - 1;
	my $piece_y = ord((split //, $piece)[1]) - 97;
	my $target_x = (split //, $target)[0] - 1;
	my $target_y = ord((split //, $target)[1]) - 97;
	
	if (not defined $array[$piece_x][$piece_y] or $array[$piece_x][$piece_y]->owner != $cur_player or $array[$piece_x][$piece_y]->alive < 1){
		return "Invalid move";
	} elsif (abs($piece_x-$target_x) + abs($piece_y-$target_y) > 1){
		return "Too far away, missed the target";
	} elsif (not defined $array[$target_x][$target_y]){
		return "Missed!";
	} else{
		$array[$target_x][$target_y]->dmg($array[$piece_x][$piece_y]->dmg());
		return "Hit!!!";
	}
}

sub ended {
	if (!grep {$_->alive() > 0} ($p2_s1,$p2_s2,$p2_s3,$p2_s4,$p2_s5)){
		return "Player 1 has won the game";
	} elsif (!grep {$_->alive() > 0} ($p1_s1,$p1_s2,$p1_s3,$p1_s4,$p1_s5)){
		return "Player 2 has won the game";
	} else {
		return 0;
	}
}

sub move {
	my $self = shift;
	my $cur_player = shift;
	my $piece = (split /\W+/, @_[0])[0];
	my $target = (split /\W+/, @_[0])[1];
	my $piece_x = (split //, $piece)[0] - 1;
	my $piece_y = ord((split //, $piece)[1]) - 97;
	my $target_x = (split //, $target)[0] - 1;
	my $target_y = ord((split //, $target)[1]) - 97;

	if (not defined $array[$piece_x][$piece_y] or $array[$piece_x][$piece_y]->owner != $cur_player or $array[$piece_x][$piece_y]->alive < 1){
		return "Invalid move";
	} elsif (abs($piece_x-$target_x) + abs($piece_y-$target_y) > 1){
		return "Too far, can't move";
	} elsif (defined $array[$target_x][$target_y]){
		return "Something is blocking the way";
	} else{
		$array[$target_x][$target_y] = $array[$piece_x][$piece_y];
		$array[$piece_x][$piece_y] = undef;
		return "Moved successfully";
	}
}

1;
