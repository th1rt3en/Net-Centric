package Ship;

sub new {
	my $class = shift;
	my $self = {@_};
	bless ($self, $class);
	
	return $self;
}

sub hp {
	my $self = shift;

	return $self->{hp};
}

sub dmg {
	my $self = shift;
	my $dmg = shift;
	$self->{hp} -= $dmg if defined $dmg;
	$self = undef if $self->{hp} <= 0;
	return $self->{dmg};
}

sub owner {
	my $self = shift;
	my $new_owner = shift;
	$self->{owner} = $new_owner if defined $new_owner;
	
	return $self->{owner};
}

1;

