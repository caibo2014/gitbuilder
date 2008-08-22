#!/usr/bin/perl -w
use strict;
use CGI qw/:standard *table start_ul/;
use POSIX qw(strftime);

use lib ".";
use Autobuilder;

my @branches = ();
my %revs = ();

sub load_revcache()
{
    open my $fh, "<revcache" 
        or return; # try to survive without it, then
    my $branch;
    my @list;
    while (<$fh>) {
	chomp;
	if (/^\:([0-9a-f]+) (.*)/) {
	    my ($newcommit, $newbranch) = ($1, $2);
	    if ($branch) {
		$revs{$branch} = join("\n", @list);
	    }
	    push @branches, "$newcommit $newbranch";
	    $branch = $newbranch;
	    @list = ();
	} else {
	    push @list, $_;
	}
    }
    if ($branch) {
	$revs{$branch} = join("\n", @list);
    }
    close $fh;
}
load_revcache();

my $currently_doing = (-f '.doing') && stripwhite(catfile(".doing"));

sub run_cmd(@)
{
    my @cmdline = @_;
    
    open(my $fh, "-|", @cmdline)
      or die("Can't run $cmdline[0]: $!\n");
    my @out = <$fh>;
    chomp @out;
    close $fh;
    return @out;
}

sub revs_for_branch($$)
{
    my ($branch, $topcommit) = @_;
    if (-x '../revlist.sh') {
	return run_cmd("../revlist.sh", $branch);
    } else {
	return split("\n", $revs{$branch});
    }
}

sub list_branches()
{
    if (-x '../branches.sh') {
	return run_cmd("../branches.sh");
    } else {
	return @branches;
    }
}

print header, start_html(
	-title => "Autobuilder results",
	-style => {-src => "index.css"}
);

print Link({-rel=>"alternate", -title=>"Autobuilder results",
	-href=>"rss.cgi", -type=>"application/rss+xml"});

print h1("Autobuilder results");

print start_table();
print Tr(th("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"),
    th("Result"), th("Commit"), th("Details"));

for my $branchinfo (list_branches()) {
    my ($topcommit, $branch) = split(" ", $branchinfo, 2);
    next if -f "ignore/$topcommit";
    my $branchprint = $branch;
    
    my $last_was_pending = 0;
    my $print_pending = 1;
    foreach my $rev (revs_for_branch($branch, $topcommit)) {
	my ($commit, $comment) = split(" ", $rev, 2);
	
	my $filename;
	my $failed;
	my $logcgi = "log.cgi?log=$commit";
	
	if (-f "pass/$commit") {
	    $filename = "pass/$commit";
	    $failed = 0;
	} elsif (-f "fail/$commit") {
	    $filename = "fail/$commit";
	    $failed = 1;
	} elsif ($commit eq $currently_doing) {
	    print Tr(td($branchprint),
		td({bgcolor=>'#ffff66'}, "BUILDING"),
		td(shorten($commit, 7)),
		td($comment));
	    $branchprint = "";
	    next;
	} elsif ($last_was_pending == 0 && $print_pending) {
	    print Tr(td($branchprint),
		td("(Pending)"),
		td(shorten($commit, 7)),
		td($comment));
	    $last_was_pending = 1;
	    $branchprint = "";
	    next;
	} else {
	    $last_was_pending++;
	    next;
	}
	    
	if ($last_was_pending > $print_pending) {
	    $last_was_pending -= $print_pending;
	    $print_pending = 0;
	    print Tr(td($branchprint),
		td("...$last_was_pending..."), td(""), td(""));
	    $branchprint = "";
	}
	$last_was_pending = 0;
    
	my $codestr = ($failed ? "Errors" : 
	    (find_errors($filename) ? "Warnings" : "ok"));
	print Tr(td($branchprint),
	    td({bgcolor=>($failed ? "#ff6666" : "#66ff66")},
		$failed ? b("FAIL") : "ok"),
	    td(shorten($commit, 7)),
	    td(a({-href=>$logcgi}, "$codestr") . " $comment"));
	$branchprint = "";
    }
    
    if ($last_was_pending > $print_pending) {
	$last_was_pending -= $print_pending;
	print Tr(td($branchprint),
	    td("...$last_was_pending..."), td(""), td(""));
	$branchprint = "";
    }
    
    print Tr(td({colspan=>4}, hr));
}

print end_table();
exit 0;
