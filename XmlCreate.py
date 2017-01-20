from lxml import etree as xml
import sys

PROJET = sys.argv[1]
BlastType = sys.argv[2].lower()

ID = "%s_%s" % (BlastType, PROJET)
NAME = "%s_%s" % (BlastType.capitalize(), PROJET)

if BlastType in ["blastx","tblastx","blastn"]: QueryLabel = "Nucleotide" 
elif BlastType in ["blastp","tblastn"]: QueryLabel = "Protein" 

if BlastType in ["blastn","tblastx","tblastn"]: 
	DbLabel = "Nucleotide" 
	LOCpublic = "blastdb.loc"
	LOC = "blastdb_%s.loc" % PROJET

elif BlastType in ["blastp","blastx"] : 
	DbLabel = "Protein"
	LOCpublic = "blastdb_p.loc"
	LOC = "blastdb_p_%s.loc" % PROJET
	
####-----HEAD---------------------------####
#xml = etree.XML('<?xml version="1.0" encoding="UTF-8"?>')

tool = xml.Element("tool", id="%s" % ID, name="%s" % NAME, version="0.0.17")

description = xml.SubElement(tool, "description")
if BlastType == "blastp" : description.text = "Search protein database with protein query sequence(s)"
elif BlastType == "blastn" : description.text = "Search nucleotide database with nucleotide query sequence(s)"
elif BlastType == "blastx" : description.text = "Search protein database with translated nucleotide query sequence(s)"
elif BlastType == "tblastx" :  description.text = "Search translated nucleotide database with translated nucleotide query sequence(s)"
elif BlastType == "tblastn" : description.text = "Search translated nucleotide database with protein query sequence(s)"

parallelism = xml.SubElement(tool, "parallelism", method="multi", split_inputs="query", split_mode="to_size", split_size="1000", shared_inputs="subject,histdb", merge_outputs="output1")

version_command = xml.SubElement(tool, "version_command")
version_command.text = "%s -version" % BlastType

####-----COMMAND------------------------####

command = xml.SubElement(tool, "command")
cmd = """
## The command is a Cheetah template which allows some Python based syntax.
## Lines starting hash hash are comments. Galaxy will turn newlines into spaces
%s
-query "$query"
#if $db_opts.db_opts_selector == "db" and $db_opts.db_type.db_type_selector == "public":
#set $dbl = " ".join(str( $db_opts.db_type.database.fields.path ).split( ',' ))
  -db "$dbl"
#elif $db_opts.db_opts_selector == "db" and $db_opts.db_type.db_type_selector == "perso":
#set $dbl = " ".join(str( $db_opts.db_type.database_p.fields.path ).split( ',' ))
  -db "$dbl"
#elif $db_opts.db_opts_selector == "histdb":
  -db "${os.path.join($db_opts.histdb.extra_files_path,'blastdb')}"
#else:
  -subject "$db_opts.subject"
#end if""" % BlastType

if BlastType in ["blastp","blastn"] : cmd +="-task $blast_type\n"
elif BlastType in ["blastx","tblastx"] : cmd += "-query_gencode $query_gencode\n"
cmd += """
-evalue $evalue_cutoff
-out $output1
##Set the extended list here so if/when we add things, saved workflows are not affected
#if str($out_format)=="ext":
    -outfmt "6 std sallseqid score nident positive gaps ppos qframe sframe qseq sseq qlen slen"
#else:
    -outfmt $out_format
#end if
-num_threads 4
#if $adv_opts.adv_opts_selector=="advanced":
$adv_opts.filter_query"""
if BlastType in ["blastx","tblastx"] : cmd += "$adv_opts.strand\n"

cmd += """
-matrix $adv_opts.matrix
## Need int(str(...)) because $adv_opts.max_hits is an InputValueWrapper object not a string
## Note -max_target_seqs overrides -num_descriptions and -num_alignments
#if (str($adv_opts.max_hits) and int(str($adv_opts.max_hits)) > 0):
-max_target_seqs $adv_opts.max_hits
#end if
#if (str($adv_opts.word_size) and int(str($adv_opts.word_size)) > 0):
-word_size $adv_opts.word_size
#end if"""

if BlastType in ["blastn","blastx"] : cmd +="$adv_opts.ungapped\n"

cmd +="""
$adv_opts.parse_deflines
## End of advanced options:
#end if""" 
command.text = cmd

####-----STDIO--------------------------####

stdio = xml.SubElement(tool, "stdio")

exit_code = xml.SubElement( stdio, "exit_code", range="1:")
exit_code2 = xml.SubElement( stdio, "exit_code", range=":-1")
regex = xml.SubElement( stdio, "regex", match="Error:")
regex2 = xml.SubElement( stdio, "regex", match="EXception:")

####-----INPUT-------------------------####

inputs = xml.SubElement(tool,"inputs")

paramQuery = xml.SubElement(inputs, "param", name="query", type="data", format="fasta", label="%s query sequence(s)" % QueryLabel)

#####################################################################################################
conditionalDb = xml.SubElement(inputs, "conditional", name="db_opts")

paramDbSelector = xml.SubElement(conditionalDb, "param", name="db_opts_selector", type="select", label="Subject database/sequences")
optionDbSelector1 = xml.SubElement(paramDbSelector, "option", value="db", selected="True")
optionDbSelector1.text = "BLAST Database"
optionDbSelector2 = xml.SubElement(paramDbSelector, "option", value="histdb")
optionDbSelector2.text = "BLAST database from your history"
optionDbSelector3 = xml.SubElement(paramDbSelector, "option", value="file")
optionDbSelector3.text = "FASTA file from your history (see warning note below)"

####
whendb = xml.SubElement(conditionalDb, "when", value="db")

#-----------------------------------------------------------------------------------------------------
conditionalDbType = xml.SubElement(whendb, "conditional", name="db_type")

paramDbTypeSelector = xml.SubElement(conditionalDbType, "param", name="db_type_selector", type="select", label="Type of DATABASE")
optionDbTypeSelector1 = xml.SubElement(paramDbTypeSelector, "option", value="public")
optionDbTypeSelector1.text = "Public databases"
optionDbTypeSelector2 = xml.SubElement(paramDbTypeSelector, "option", value="perso", selected="True")
optionDbTypeSelector2.text = "Personal project databases"

########
whenPublic = xml.SubElement(conditionalDbType, "when", value="public")

paramDatabasePublic1 = xml.SubElement(whenPublic, "param", name="database", type="select", label="%s BLAST database" % DbLabel, multiple="true")
optionDatabasePublic = xml.SubElement(paramDatabasePublic1, "options", from_file="%s" % LOCpublic)
columnOptionDatabasePublic1 = xml.SubElement(optionDatabasePublic, "column", name="value", index="0")
columnOptionDatabasePublic2 = xml.SubElement(optionDatabasePublic, "column", name="name", index="1")
columnOptionDatabasePublic3 = xml.SubElement(optionDatabasePublic, "column", name="path", index="2")

paramDatabasePerso1 = xml.SubElement(whenPublic, "param", name="database_p", type="hidden", value="")

########
whenPerso = xml.SubElement(conditionalDbType, "when", value="perso")

paramDatabasePublic2 = xml.SubElement(whenPerso, "param", name="database", type="hidden", value="")

paramDatabasePerso2 = xml.SubElement(whenPerso, "param", name="database_p", type="select", label="%s BLAST database" % DbLabel, multiple="true", size="5x35")
optionDatabasePerso = xml.SubElement(paramDatabasePerso2, "options", from_file="%s" % LOC)
columnOpDatabasePerso1 = xml.SubElement(optionDatabasePerso, "column", name="value", index="0")
columnOpDatabasePerso2 = xml.SubElement(optionDatabasePerso, "column", name="name", index="1")
columnOpDatabasePerso3 = xml.SubElement(optionDatabasePerso, "column", name="path", index="2")
#-----------------------------------------------------------------------------------------------------

paramHistdb1 = xml.SubElement(whendb, "param", name="histdb", type="hidden", value="")
paramSubject1 = xml.SubElement(whendb, "param", name="subject", type="hidden", value="")

####
whenHistdb = xml.SubElement(conditionalDb, "when", value="histdb")

paramDatabasePublic3 = xml.SubElement(whenHistdb, "param", name="database", type="hidden", value="")
paramDatabasePerso3 = xml.SubElement(whenHistdb, "param", name="database_p", type="hidden", value="")
paramHistdb2 = xml.SubElement(whenHistdb, "param", name="histdb", type="data", format="blastdbp", label="%s BLAST database" % DbLabel)
paramSubject2 = xml.SubElement(whenHistdb, "param", name="subject", type="hidden", value="")

####
whenFile = xml.SubElement(conditionalDb, "when", value="file")

paramDatabasePublic4 = xml.SubElement(whenFile, "param", name="database", type="hidden", value="")
paramDatabasePerso4 = xml.SubElement(whenFile, "param", name="database_p", type="hidden", value="")
paramHistdb3 = xml.SubElement(whenFile, "param", name="histdb", type="hidden", value="")
paramSubject3 = xml.SubElement(whenFile, "param", name="subject", type="data", format="fasta", label="%s FASTA file to use as database" % DbLabel )
#####################################################################################################

if BlastType in ["blastp","blastn"] :
	paramBlastType = xml.SubElement(inputs, "param", name="blast_type", type="select", display="radio", label="Type of BLAST")
	
	if BlastType == "blastp" :
		optionBlastType1 = xml.SubElement(paramBlastType, "option", value="blastp")
		optionBlastType1.text = "blastp"
		optionBlastType2 = xml.SubElement(paramBlastType, "option", value="blastp-short")
		optionBlastType2.text = "blastp-short"
	elif BlastType == "blastn" :
		optionBlastType1 = xml.SubElement(paramBlastType, "option", value="megablast")
		optionBlastType1.text = "megablast"
		optionBlastType2 = xml.SubElement(paramBlastType, "option", value="blastn")
		optionBlastType2.text = "blastn"
		optionBlastType3 = xml.SubElement(paramBlastType, "option", value="blastn-short")
		optionBlastType3.text = "blastn-short"
		optionBlastType4 = xml.SubElement(paramBlastType, "option", value="dc-megablast")
		optionBlastType4.text = "dc-megablast"

if BlastType in ["blastx","tblastx"] :
	paramcode = xml.SubElement(inputs, "param", name="query_gencode", type="select", label="Query genetic code")

	optionCode1 = xml.SubElement(paramcode, "option", value="1", select = "True")
	optionCode1.text = "1. Standard"
	optionCode2 = xml.SubElement(paramcode, "option", value="2")
	optionCode2.text = "2. Vertebrate Mitochondrial"
	optionCode3 = xml.SubElement(paramcode, "option", value="3")
	optionCode3.text = "3. Yeast Mitochondrial"
	optionCode4 = xml.SubElement(paramcode, "option", value="4")
	optionCode4.text = "4. Mold, Protozoan, and Coelenterate Mitochondrial Code and the Mycoplasma/Spiroplasma Code"
	optionCode5 = xml.SubElement(paramcode, "option", value="5")
	optionCode5.text = "5. Invertebrate Mitochondrial"
	optionCode6 = xml.SubElement(paramcode, "option", value="6")
	optionCode6.text = "6. Ciliate, Dasycladacean and Hexamita Nuclear Code"
	optionCode7 = xml.SubElement(paramcode, "option", value="9")
	optionCode7.text = "9. Echinoderm Mitochondrial"
	optionCode8 = xml.SubElement(paramcode, "option", value="10")
	optionCode8.text = "10. Euplotid Nuclear"
	optionCode9 = xml.SubElement(paramcode, "option", value="11")
	optionCode9.text = "11. Bacteria and Archaea"
	optionCode10 = xml.SubElement(paramcode, "option", value="12")
	optionCode10.text = "12. Alternative Yeast Nuclear"
	optionCode11 = xml.SubElement(paramcode, "option", value="13")
	optionCode11.text = "13. Ascidian Mitochondrial"
	optionCode12 = xml.SubElement(paramcode, "option", value="14")
	optionCode12.text = "14. Flatworm Mitochondrial"
	optionCode13 = xml.SubElement(paramcode, "option", value="15")
	optionCode13.text = "15. Blepharisma Macronuclear"
	optionCode14 = xml.SubElement(paramcode, "option", value="16")
	optionCode14.text = "16. Chlorophycean Mitochondrial Code"
	optionCode15 = xml.SubElement(paramcode, "option", value="21")
	optionCode15.text = "21. Trematode Mitochondrial Code"
	optionCode16 = xml.SubElement(paramcode, "option", value="22")
	optionCode16.text = "22. Scenedesmus obliquus mitochondrial Code"
	optionCode17 = xml.SubElement(paramcode, "option", value="23")
	optionCode17.text = "23. Thraustochytrium Mitochondrial Code"
	optionCode18 = xml.SubElement(paramcode, "option", value="24")
	optionCode18.text = "24. Pterobranchia mitochondrial code"

paramEvalue = xml.SubElement(inputs, "param", name="evalue_cutoff", type="float", size="15", value="0.001", label="Set expectation value cutoff")

paramOut_Format = xml.SubElement(inputs, "param", name="out_format", type="select", label="Output format")
optionOut_Format1 = xml.SubElement(paramOut_Format, "option", value="6")
optionOut_Format1.text = "Tabular (standard 12 columns)"
optionOut_Format2 = xml.SubElement(paramOut_Format, "option", value="ext", selected="True")
optionOut_Format2.text = "Tabular (extended 24 columns)"
optionOut_Format3 = xml.SubElement(paramOut_Format, "option", value="5")
optionOut_Format3.text = "BLAST XML"
optionOut_Format4 = xml.SubElement(paramOut_Format, "option", value="0")
optionOut_Format4.text = "Pairwise text"
optionOut_Format5 = xml.SubElement(paramOut_Format, "option", value="0 -html")
optionOut_Format5.text = "Pairwise HTML"
optionOut_Format6 = xml.SubElement(paramOut_Format, "option", value="2")
optionOut_Format6.text = "Query-anchored text"
optionOut_Format7 = xml.SubElement(paramOut_Format, "option", value="2 -html")
optionOut_Format7.text = "Query-anchored HTML"
optionOut_Format8 = xml.SubElement(paramOut_Format, "option", value="4")
optionOut_Format8.text = "Flat query-anchored text"
optionOut_Format9 = xml.SubElement(paramOut_Format, "option", value="4 - html")
optionOut_Format9.text = "Flat query-anchored HTML"
optionOut_Format10 = xml.SubElement(paramOut_Format, "option", value="11")
optionOut_Format10.text = "BLAST archive format (ASN.1)"	

#####################################################################################################
conditionalAdv = xml.SubElement(inputs, "conditional", name="adv_opts")

paramAdvSelec = xml.SubElement(conditionalAdv, "param", name="adv_opts_selector", type="select", label="Advanced Options")

optionAdvSelec1 = xml.SubElement(paramAdvSelec, "option", value="basic", selected="True")
optionAdvSelec1.text = "Hide Advanced Options"
optionAdvSelec2 = xml.SubElement(paramAdvSelec, "option", value="advanced")
optionAdvSelec2.text = "Show Advanced Options"

####
whenBasic = xml.SubElement(conditionalAdv, "when", value="basic")

####
whenAdv = xml.SubElement(conditionalAdv, "when", value="advanced")

if BlastType in ["tblastn","tblastx"] :
	paramdbcode = xml.SubElement(whenAdv, "param", name="db_gencode", type="select", label="Database/subject genetic code")

	optiondbcode1 = xml.SubElement(paramdbcode, "option", value="1", select = "True")
	optiondbcode1.text = "1. Standard"
	optiondbcode2 = xml.SubElement(paramdbcode, "option", value="2")
	optiondbcode2.text = "2. Vertebrate Mitochondrial"
	optiondbcode3 = xml.SubElement(paramdbcode, "option", value="3")
	optiondbcode3.text = "3. Yeast Mitochondrial"
	optiondbcode4 = xml.SubElement(paramdbcode, "option", value="4")
	optiondbcode4.text = "4. Mold, Protozoan, and Coelenterate Mitochondrial Code and the Mycoplasma/Spiroplasma Code"
	optiondbcode5 = xml.SubElement(paramdbcode, "option", value="5")
	optiondbcode5.text = "5. Invertebrate Mitochondrial"
	optiondbcode6 = xml.SubElement(paramdbcode, "option", value="6")
	optiondbcode6.text = "6. Ciliate, Dasycladacean and Hexamita Nuclear Code"
	optiondbcode7 = xml.SubElement(paramdbcode, "option", value="9")
	optiondbcode7.text = "9. Echinoderm Mitochondrial"
	optiondbcode8 = xml.SubElement(paramdbcode, "option", value="10")
	optiondbcode8.text = "10. Euplotid Nuclear"
	optiondbcode9 = xml.SubElement(paramdbcode, "option", value="11")
	optiondbcode9.text = "11. Bacteria and Archaea"
	optiondbcode10 = xml.SubElement(paramdbcode, "option", value="12")
	optiondbcode10.text = "12. Alternative Yeast Nuclear"
	optiondbcode11 = xml.SubElement(paramdbcode, "option", value="13")
	optiondbcode11.text = "13. Ascidian Mitochondrial"
	optiondbcode12 = xml.SubElement(paramdbcode, "option", value="14")
	optiondbcode12.text = "14. Flatworm Mitochondrial"
	optiondbcode13 = xml.SubElement(paramdbcode, "option", value="15")
	optiondbcode13.text = "15. Blepharisma Macronuclear"
	optiondbcode14 = xml.SubElement(paramdbcode, "option", value="16")
	optiondbcode14.text = "16. Chlorophycean Mitochondrial Code"
	optiondbcode15 = xml.SubElement(paramdbcode, "option", value="21")
	optiondbcode15.text = "21. Trematode Mitochondrial Code"
	optiondbcode16 = xml.SubElement(paramdbcode, "option", value="22")
	optiondbcode16.text = "22. Scenedesmus obliquus mitochondrial Code"
	optiondbcode17 = xml.SubElement(paramdbcode, "option", value="23")
	optiondbcode17.text = "23. Thraustochytrium Mitochondrial Code"
	optiondbcode18 = xml.SubElement(paramdbcode, "option", value="24")
	optiondbcode18.text = "24. Pterobranchia mitochondrial code"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if BlastType == "blastn" : paramFilter = xml.SubElement(whenAdv, "param", name="filter_query", type="boolean", label="Filter out low complexity regions (with DUST)", truevalue="-dust yes", falsevalue="-dust no", checked="true")

else :paramFilter = xml.SubElement(whenAdv, "param", name="filter_query", type="boolean", label="Filter out low complexity regions (with SEG)", truevalue="-seg yes", falsevalue="-seg no", checked="false")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if BlastType in ["blastn","blastx","blastx"] :
	paramstrand = xml.SubElement(whenAdv, "param", name="strand", type="select", label="Query strand(s) to search against database/subject")

	optionStrand1 = xml.SubElement(paramstrand, "option", value="-strand both")
	optionStrand1.text = "Both"
	optionStrand2 = xml.SubElement(paramstrand, "option", value="-strand plus")
	optionStrand2.text = "Plus (forward)"
	optionStrand3 = xml.SubElement(paramstrand, "option", value="-strand minus")
	optionStrand3.text = "Minus (reverse complement)"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
if BlastType != "blastn" :

	paramMatrix = xml.SubElement(whenAdv, "param", name="matrix", type="select", label="Scoring matrix")
	optionMatrix1 = xml.SubElement(paramMatrix, "option", value="BLOSUM90")
	optionMatrix1.text = "BLOSUM90"
	optionMatrix2 = xml.SubElement(paramMatrix, "option", value="BLOSUM80")
	optionMatrix2.text = "BLOSUM80"
	optionMatrix3 = xml.SubElement(paramMatrix, "option", value="BLOSUM62", selected="True")
	optionMatrix3.text = "BLOSUM62 (default)"
	optionMatrix4 = xml.SubElement(paramMatrix, "option", value="BLOSUM50")
	optionMatrix4.text = "BLOSUM50"
	optionMatrix5 = xml.SubElement(paramMatrix, "option", value="BLOSUM45")
	optionMatrix5.text = "BLOSUM45"
	optionMatrix6 = xml.SubElement(paramMatrix, "option", value="PAM250")
	optionMatrix6.text = "PAM250"
	optionMatrix7 = xml.SubElement(paramMatrix, "option", value="PAM70")
	optionMatrix7.text = "PAM70"
	optionMatrix8 = xml.SubElement(paramMatrix, "option", value="PAM30")
	optionMatrix8.text = "PAM30"

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
paramMaxHits = xml.SubElement(whenAdv, "param", name="max_hits", type="integer", value="0", label="Maximum hits to show", help="Use zero for default limits")
validatorMaxHits = xml.SubElement(paramMaxHits, "validator", type="in_range", min="0")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
paramWordSize = xml.SubElement(whenAdv, "param", name="word_size", type="integer", value="0", label="Word size for wordfinder algorithm", help="Use zero for default, otherwise minimum 2.")
validatorWordSize = xml.SubElement(paramWordSize, "validator", type="in_range", min="0")

if BlastType in ["blastn", "blastx" ] : paramUngap =  xml.SubElement(whenAdv, "param", name="ungapped", type="boolean", label="Perform ungapped alignment only?", truevalue="-ungapped", falsevalue="", checked="false")
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
paramParse = xml.SubElement(whenAdv, "param", name="parse_deflines", type="boolean", label="Should the query and subject defline(s) be parsed?", truevalue="-parse_deflines", falsevalue="", checked="false", help="This affects the formatting of the query/subject ID strings")

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
paramLabel = xml.SubElement(inputs, "param", name="label", type="text", value="%s" % BlastType.capitalize(), label="Output Name")

####-----OUTPUT-------------------------####

outputs = xml.SubElement(tool, "outputs")

data = xml.SubElement(outputs, "data", name="output1", format="tabular", label="$label")

change_format = xml.SubElement(data, "change_format")

whenOut1 = xml.SubElement(change_format, "when", input="out_format", value="0", format="txt")
whenOut2 = xml.SubElement(change_format, "when", input="out_format", value="0 -html", format="html")
whenOut3 = xml.SubElement(change_format, "when", input="out_format", value="2", format="txt")
whenOut4 = xml.SubElement(change_format, "when", input="out_format", value="2 -html", format="html")
whenOut5 = xml.SubElement(change_format, "when", input="out_format", value="4", format="txt")
whenOut6 = xml.SubElement(change_format, "when", input="out_format", value="4 -html", format="html")
whenOut7 = xml.SubElement(change_format, "when", input="out_format", value="5", format="blastxml")
whenOut8 = xml.SubElement(change_format, "when", input="out_format", value="11", format="tabular")

####-----REQUIREMENTS------------------####

requirements = xml.SubElement(tool, "requirements")

requirement = xml.SubElement(requirements, "requirement", type="binary")
requirement.text = "%s" % BlastType

####-----TESTS-------------------------####

if BlastType == "blastp" :
	tests = xml.SubElement(tool, "tests")

	test1 = xml.SubElement(tests, "test")

	paramt11 = xml.SubElement(test1, "param", name="query", value="four_human_proteins.fasta", ftype="fasta")
	paramt12 = xml.SubElement(test1, "param", name="db_opts_selector", value="file")
	paramt13 = xml.SubElement(test1, "param", name="subject", value="rhodopsin_proteins.fasta", ftype="fasta")
	paramt14 = xml.SubElement(test1, "param", name="database", value="")
	paramt15 = xml.SubElement(test1, "param", name="evalue_cutoff", value="1e-8")
	paramt16 = xml.SubElement(test1, "param", name="blast_type", value="blastp")
	paramt17 = xml.SubElement(test1, "param", name="out_format", value="5")
	paramt18 = xml.SubElement(test1, "param", name="adv_opts_selector", value="advanced")
	paramt19 = xml.SubElement(test1, "param", name="filter_query", value="False")
	paramt110 = xml.SubElement(test1, "param", name="matrix", value="BLOSUM62")
	paramt111 = xml.SubElement(test1, "param", name="max_hits", value="0")
	paramt112 = xml.SubElement(test1, "param", name="word_size", value="0")
	paramt113 = xml.SubElement(test1, "param", name="parse_deflines", value="True")
	outputt11 = xml.SubElement(test1, "output", name="output1", file="blastp_four_human_vs_rhodopsin.xml", ftype="blastxml")

	test2 = xml.SubElement(tests, "test")

	paramt21 = xml.SubElement(test2, "param", name="query", value="four_human_proteins.fasta", ftype="fasta")
	paramt22 = xml.SubElement(test2, "param", name="db_opts_selector", value="file")
	paramt23 = xml.SubElement(test2, "param", name="subject", value="rhodopsin_proteins.fasta", ftype="fasta")
	paramt24 = xml.SubElement(test2, "param", name="database", value="")
	paramt25 = xml.SubElement(test2, "param", name="evalue_cutoff", value="1e-18")
	paramt26 = xml.SubElement(test2, "param", name="blast_type", value="blastp")
	paramt27 = xml.SubElement(test2, "param", name="out_format", value="6")
	paramt28 = xml.SubElement(test2, "param", name="adv_opts_selector", value="advanced")
	paramt29 = xml.SubElement(test2, "param", name="filter_query", value="False")
	paramt210 = xml.SubElement(test2, "param", name="matrix", value="BLOSUM62")
	paramt211 = xml.SubElement(test2, "param", name="max_hits", value="0")
	paramt212 = xml.SubElement(test2, "param", name="word_size", value="0")
	paramt213 = xml.SubElement(test2, "param", name="parse_deflines", value="True")
	outputt21 = xml.SubElement(test2, "output", name="output1", file="blastp_four_human_vs_rhodopsin.tabular", ftype="tabular")

	test3 = xml.SubElement(tests, "test")

	paramt31 = xml.SubElement(test3, "param", name="query", value="four_human_proteins.fasta", ftype="fasta")
	paramt32 = xml.SubElement(test3, "param", name="db_opts_selector", value="file")
	paramt33 = xml.SubElement(test3, "param", name="subject", value="rhodopsin_proteins.fasta", ftype="fasta")
	paramt34 = xml.SubElement(test3, "param", name="database", value="")
	paramt35 = xml.SubElement(test3, "param", name="evalue_cutoff", value="1e-8")
	paramt36 = xml.SubElement(test3, "param", name="blast_type", value="blastp")
	paramt37 = xml.SubElement(test3, "param", name="out_format", value="ext")
	paramt38 = xml.SubElement(test3, "param", name="adv_opts_selector", value="advanced")
	paramt39 = xml.SubElement(test3, "param", name="filter_query", value="False")
	paramt310 = xml.SubElement(test3, "param", name="matrix", value="BLOSUM62")
	paramt311 = xml.SubElement(test3, "param", name="max_hits", value="0")
	paramt312 = xml.SubElement(test3, "param", name="word_size", value="0")
	paramt313 = xml.SubElement(test3, "param", name="parse_deflines", value="True")
	outputt31 = xml.SubElement(test3, "output", name="output1", file="blastp_four_human_vs_rhodopsin_ext.tabular", ftype="tabular")

	test4 = xml.SubElement(tests, "test")

	paramt41 = xml.SubElement(test3, "param", name="query", value="rhodopsin_proteins.fasta", ftype="fasta")
	paramt42 = xml.SubElement(test3, "param", name="db_opts_selector", value="file")
	paramt43 = xml.SubElement(test3, "param", name="subject", value="four_human_proteins.fasta", ftype="fasta")
	paramt44 = xml.SubElement(test3, "param", name="database", value="")
	paramt45 = xml.SubElement(test3, "param", name="evalue_cutoff", value="1e-8")
	paramt46 = xml.SubElement(test3, "param", name="blast_type", value="blastp")
	paramt47 = xml.SubElement(test3, "param", name="out_format", value="6")
	paramt48 = xml.SubElement(test3, "param", name="adv_opts_selector", value="basic")
	outputt41 = xml.SubElement(test3, "output", name="output1", file="blastp_rhodopsin_vs_four_human.tabular", ftype="tabular")

if BlastType == "blastx" :

	tests = xml.SubElement(tool, "tests")

	test1 = xml.SubElement(tests, "test")

	paramt11 = xml.SubElement(test1, "param", name="query", value="rhodopsin_nucs.fasta", ftype="fasta")
	paramt12 = xml.SubElement(test1, "param", name="db_opts_selector", value="file")
	paramt13 = xml.SubElement(test1, "param", name="subject", value="four_human_proteins.fasta", ftype="fasta")
	paramt14 = xml.SubElement(test1, "param", name="database", value="")
	paramt15 = xml.SubElement(test1, "param", name="evalue_cutoff", value="1e-10")
	paramt16 = xml.SubElement(test1, "param", name="out_format", value="5")
	paramt17 = xml.SubElement(test1, "param", name="adv_opts_selector", value="basic")
	outputt11 = xml.SubElement(test1, "output", name="output1", file="blastx_rhodopsin_vs_four_human.xml", ftype="blastxml")

	test2 = xml.SubElement(tests, "test")

	paramt21 = xml.SubElement(test2, "param", name="query", value="rhodopsin_nucs.fasta", ftype="fasta")
	paramt22 = xml.SubElement(test2, "param", name="db_opts_selector", value="file")
	paramt23 = xml.SubElement(test2, "param", name="subject", value="four_human_proteins.fasta", ftype="fasta")
	paramt24 = xml.SubElement(test2, "param", name="database", value="")
	paramt25 = xml.SubElement(test2, "param", name="evalue_cutoff", value="1e-10")
	paramt26 = xml.SubElement(test2, "param", name="out_format", value="6")
	paramt27 = xml.SubElement(test2, "param", name="adv_opts_selector", value="basic")
	outputt21 = xml.SubElement(test2, "output", name="output1", file="blastx_rhodopsin_vs_four_human.tabular", ftype="tabular")

	test3 = xml.SubElement(tests, "test")

	paramt31 = xml.SubElement(test3, "param", name="query", value="rhodopsin_nucs.fasta", ftype="fasta")
	paramt32 = xml.SubElement(test3, "param", name="db_opts_selector", value="file")
	paramt33 = xml.SubElement(test3, "param", name="subject", value="four_human_proteins.fasta", ftype="fasta")
	paramt34 = xml.SubElement(test3, "param", name="database", value="")
	paramt35 = xml.SubElement(test3, "param", name="evalue_cutoff", value="1e-10")
	paramt36 = xml.SubElement(test3, "param", name="out_format", value="ext")
	paramt37 = xml.SubElement(test3, "param", name="adv_opts_selector", value="basic")
	outputt31 = xml.SubElement(test3, "output", name="output1", file="blastx_rhodopsin_vs_four_human_ext.tabular", ftype="tabular")

if BlastType == "tblastn" :

	tests = xml.SubElement(tool, "tests")

	test1 = xml.SubElement(tests, "test")

	paramt11 = xml.SubElement(test1, "param", name="query", value="four_human_proteins.fasta", ftype="fasta")
	paramt12 = xml.SubElement(test1, "param", name="db_opts_selector", value="file")
	paramt13 = xml.SubElement(test1, "param", name="subject", value="rhodopsin_nucs.fasta", ftype="fasta")
	paramt14 = xml.SubElement(test1, "param", name="database", value="")
	paramt15 = xml.SubElement(test1, "param", name="evalue_cutoff", value="1e-10")
	paramt16 = xml.SubElement(test1, "param", name="out_format", value="5")
	paramt17 = xml.SubElement(test1, "param", name="adv_opts_selector", value="advanced")
	paramt18 = xml.SubElement(test1, "param", name="filter_query", value="false")
	paramt19 = xml.SubElement(test1, "param", name="matrix", value="BLOSUM80")
	paramt110 = xml.SubElement(test1, "param", name="max_hits", value="0")
	paramt111 = xml.SubElement(test1, "param", name="word_size", value="0")
	paramt112 = xml.SubElement(test1, "param", name="parse_deflines", value="false")
	outputt11 = xml.SubElement(test1, "output", name="output1", file="tblastn_four_human_vs_rhodopsin.xml", ftype="blastxml")

	test2 = xml.SubElement(tests, "test")
	paramt21 = xml.SubElement(test2, "param", name="query", value="four_human_proteins.fasta", ftype="fasta" )
	paramt22 = xml.SubElement(test2, "param", name="db_opts_selector", value="file" )
	paramt23 = xml.SubElement(test2, "param", name="subject", value="rhodopsin_nucs.fasta", ftype="fasta" )
	paramt24 = xml.SubElement(test2, "param", name="database", value="" )
	paramt25 = xml.SubElement(test2, "param", name="evalue_cutoff", value="1e-10" )
	paramt26 = xml.SubElement(test2, "param", name="out_format", value="ext" )
	paramt27 = xml.SubElement(test2, "param", name="adv_opts_selector", value="advanced" )
	paramt28 = xml.SubElement(test2, "param", name="filter_query", value="false" )
	paramt29 = xml.SubElement(test2, "param", name="matrix", value="BLOSUM80" )
	paramt210 = xml.SubElement(test2, "param", name="max_hits", value="0" )
	paramt211 = xml.SubElement(test2, "param", name="word_size", value="0" )
	paramt212 = xml.SubElement(test2, "param", name="parse_deflines", value="false" )
	outputt21 = xml.SubElement(test2, "output", name="output1", file="tblastn_four_human_vs_rhodopsin_ext.tabular", ftype="tabular" )

	test3 = xml.SubElement(tests, "test")
	paramt31 = xml.SubElement(test3, "param", name="query", value="four_human_proteins.fasta", ftype="fasta" )
	paramt32 = xml.SubElement(test3, "param", name="db_opts_selector", value="file" )
	paramt33 = xml.SubElement(test3, "param", name="subject", value="rhodopsin_nucs.fasta", ftype="fasta" )
	paramt34 = xml.SubElement(test3, "param", name="database", value="" )
	paramt35 = xml.SubElement(test3, "param", name="evalue_cutoff", value="1e-10" )
	paramt36 = xml.SubElement(test3, "param", name="out_format", value="6" )
	paramt37 = xml.SubElement(test3, "param", name="adv_opts_selector", value="advanced" )
	paramt38 = xml.SubElement(test3, "param", name="filter_query", value="false" )
	paramt39 = xml.SubElement(test3, "param", name="matrix", value="BLOSUM80" )
	paramt310 = xml.SubElement(test3, "param", name="max_hits", value="0" )
	paramt311 = xml.SubElement(test3, "param", name="word_size", value="0" )
	paramt312 = xml.SubElement(test3, "param", name="parse_deflines", value="false" )
	outputt31 = xml.SubElement(test3, "output", name="output1", file="tblastn_four_human_vs_rhodopsin.tabular", ftype="tabular" )

	test4 = xml.SubElement(tests, "test")
	paramt41 = xml.SubElement(test4, "param", name="query", value="four_human_proteins.fasta", ftype="fasta" )
	paramt42 = xml.SubElement(test4, "param", name="db_opts_selector", value="file" )
	paramt43 = xml.SubElement(test4, "param", name="subject", value="rhodopsin_nucs.fasta", ftype="fasta" )
	paramt44 = xml.SubElement(test4, "param", name="database", value="" )
	paramt45 = xml.SubElement(test4, "param", name="evalue_cutoff", value="1e-10" )
	paramt46 = xml.SubElement(test4, "param", name="out_format", value="6" )
	paramt47 = xml.SubElement(test4, "param", name="adv_opts_selector", value="advanced" )
	paramt48 = xml.SubElement(test4, "param", name="filter_query", value="false" )
	paramt49 = xml.SubElement(test4, "param", name="matrix", value="BLOSUM80" )
	paramt410 = xml.SubElement(test4, "param", name="max_hits", value="0" )
	paramt411 = xml.SubElement(test4, "param", name="word_size", value="0" )
	paramt412 = xml.SubElement(test4, "param", name="parse_deflines", value="true" )
	outputt41 = xml.SubElement(test4, "output", name="output1", file="tblastn_four_human_vs_rhodopsin.tabular", ftype="tabular" )

	test5 = xml.SubElement(tests, "test")
	paramt51 = xml.SubElement(test5, "param", name="query", value="four_human_proteins.fasta", ftype="fasta" )
	paramt52 = xml.SubElement(test5, "param", name="db_opts_selector", value="file" )
	paramt53 = xml.SubElement(test5, "param", name="subject", value="rhodopsin_nucs.fasta", ftype="fasta" )
	paramt54 = xml.SubElement(test5, "param", name="database", value="" )
	paramt55 = xml.SubElement(test5, "param", name="evalue_cutoff", value="1e-10" )
	paramt56 = xml.SubElement(test5, "param", name="out_format", value="0 -html" )
	paramt57 = xml.SubElement(test5, "param", name="adv_opts_selector", value="advanced" )
	paramt58 = xml.SubElement(test5, "param", name="filter_query", value="false" )
	paramt59 = xml.SubElement(test5, "param", name="matrix", value="BLOSUM80" )
	paramt510 = xml.SubElement(test5, "param", name="max_hits", value="0" )
	paramt511 = xml.SubElement(test5, "param", name="word_size", value="0" )
	paramt512 = xml.SubElement(test5, "param", name="parse_deflines", value="false" )
	outputt51 = xml.SubElement(test5, "output", name="output1", file="tblastn_four_human_vs_rhodopsin.html", ftype="html" )
####-----HELP--------------------------####

help = xml.SubElement(tool, "help")
help.text =  """
.. class:: warningmark

**Note**. Database searches may take a substantial amount of time.
For large input datasets it is advisable to allow overnight processing.  

-----

**What it does**

Search a *protein database* using a *protein query*,
using the NCBI BLAST+ blastp command line tool.

.. class:: warningmark

You can also search against a FASTA file of subject protein
sequences. This is *not* advised because it is slower (only one
CPU is used), but more importantly gives e-values for pairwise
searches (very small e-values which will look overly signficiant).
In most cases you should instead turn the other FASTA file into a
database first using *makeblastdb* and search against that.

-----

**Output format**

Because Galaxy focuses on processing tabular data, the default output of this
tool is tabular. The standard BLAST+ tabular output contains 12 columns:

====== ========= ============================================
Column NCBI name Description
------ --------- --------------------------------------------
     1 qseqid    Query Seq-id (ID of your sequence)
     2 sseqid    Subject Seq-id (ID of the database hit)
     3 pident    Percentage of identical matches
     4 length    Alignment length
     5 mismatch  Number of mismatches
     6 gapopen   Number of gap openings
     7 qstart    Start of alignment in query
     8 qend      End of alignment in query
     9 sstart    Start of alignment in subject (database hit)
    10 send      End of alignment in subject (database hit)
    11 evalue    Expectation value (E-value)
    12 bitscore  Bit score
====== ========= ============================================

The BLAST+ tools can optionally output additional columns of information,
but this takes longer to calculate. Most (but not all) of these columns are
included by selecting the extended tabular output. The extra columns are
included *after* the standard 12 columns. This is so that you can write
workflow filtering steps that accept either the 12 or 24 column tabular
BLAST output. Galaxy now uses this extended 24 column output by default.

====== ============= ===========================================
Column NCBI name     Description
------ ------------- -------------------------------------------
    13 sallseqid     All subject Seq-id(s), separated by a ';'
    14 score         Raw score
    15 nident        Number of identical matches
    16 positive      Number of positive-scoring matches
    17 gaps          Total number of gaps
    18 ppos          Percentage of positive-scoring matches
    19 qframe        Query frame
    20 sframe        Subject frame
    21 qseq          Aligned part of query sequence
    22 sseq          Aligned part of subject sequence
    23 qlen          Query sequence length
    24 slen          Subject sequence length
====== ============= ===========================================

The third option is BLAST XML output, which is designed to be parsed by
another program, and is understood by some Galaxy tools.

You can also choose several plain text or HTML output formats which are designed to be read by a person (not by another program).
The HTML versions use basic webpage formatting and can include links to the hits on the NCBI website.
The pairwise output (the default on the NCBI BLAST website) shows each match as a pairwise alignment with the query.
The two query anchored outputs show a multiple sequence alignment between the query and all the matches,
and differ in how insertions are shown (marked as insertions or with gap characters added to the other sequences).

-------

**References**

Altschul et al. Gapped BLAST and PSI-BLAST: a new generation of protein database search programs. 1997. Nucleic Acids Res. 25:3389-3402.

Schaffer et al. Improving the accuracy of PSI-BLAST protein database searches with composition-based statistics and other refinements. 2001. Nucleic Acids Res. 29:2994-3005.
"""
print(xml.tostring(tool, pretty_print=True))














