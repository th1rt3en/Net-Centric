my %hash;
open(my $file, '<:encoding(UTF-8)', "listofstring.txt");
while (my $row = <$file>) {
	chomp $row;
	if (exists $hash{$row}) {
		$hash{$row} += 1;
	} else {
		$hash{$row} = 1;
	}
}
print "$_ $hash{$_}\n" for (keys %hash);
