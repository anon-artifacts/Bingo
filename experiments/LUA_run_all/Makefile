SHELL:= /bin/bash#
.SILENT: # no output

LOUD = \033[1;34m#
HIGH = \033[1;33m#
SOFT = \033[0m#

help: ## show help
	grep '^[a-z].*:.*##' $(MAKEFILE_LIST) \
	| sort \
	| gawk 'BEGIN {FS="##"; print "\n$(LOUD)make$(SOFT) [OPTIONS]\n"} \
	              {sub(/:.*/,"",$$1); \
                 printf("$(LOUD)%10s$(SOFT) %s\n",$$1,$$2)}'
	echo -e "$(HIGH)"; cat ../etc/frog.txt; echo -e "$(SOFT)"

vim: ## vim install
	mkdir -p ~/.vim
	if [[ ! -d ~/.vim/bundle ]]; \
	then git clone https://github.com/VundleVim/Vundle.vim.git ~/.vim/bundle/Vundle.vim; \
	fi
	vim +'PluginInstall --sync' +qa

sh: ## run a shell
	bash --init-file  ../etc/dotshellrc -i

push: ## commit to main
	- echo -en "$(LOUD)Why this push? $(SOFT)" ;  read x ; git commit -am "$$x" ;  git push
	- git status

word: ## commit to main
	- echo -en "$(LOUD)phrase? $(SOFT)" ;  read x ; figlet -W -f mini $$x | gawk '{print "-- " $$0}' |pbcopy

../docs/%.html : ../src/%.md    
	1>&2 echo "... $@"
	sed -e '1d' -e '2d' $< | pandoc  -o $@ $(Pandoc)

~/tmp/%.html : %.lua
	pycco -d ~/tmp $^
	echo "p { text-align: right; }" >> ~/tmp/pycco.css
	open $@

../docs/%.html : %.lua
	pycco -d ../docs  $^
	echo "p { text-align: right;  }  " >> ../docs/pycco.css
	gawk '/<h1>/ {print "<div class=docs>";                       \
                while(getline x < "../etc/head.html") {print x}; \
                print "<h1>'$^'</h1></div>";                  \
                next} 1' $@ > tmp.tmp
	mv tmp.tmp $@

~/tmp/%.pdf : %.lua  Makefile
	@mkdir -p docs
	@echo "pdfing : $@ ... "
	@a2ps -Bj --landscape                           \
		--chars-per-line=90 \
		--line-numbers=1                    \
		--highlight-level=normal  \
		--columns 3                 \
		--borders=no --pro=color \
		--right-footer="" --left-footer=""    \
		--pretty-print=../etc/lua.ssh             \
		--footer="page %p."                     \
		-M letter -o $@.ps $<
	@ps2pdf $@.ps $@; rm $@.ps

heading:
	- echo -en "$(LOUD)Heading? $(SOFT)" ;  read x ; figlet -W -f mini $$x | gawk '{print "#  " $$0}'

comparez: ../../data/moot/optimize/[bchm]*/*.csv
	echo -n "" > comparez.out
	$(foreach f, $^, (lua run_all.lua --comparez $f >> $@.out& ); )

branch: ../../data/moot/optimize/[bchm]*/*.csv
	$(foreach f, $^, (lua run_all.lua --branch $f | sort -rn | fmt -100  &) ; )

branches:; $(MAKE) branch | tee ~/tmp/$@.out
comparezs:; $(MAKE) comparez | tee $@.out

report:
	    @mkdir -p ../../results/optimization_performance; \
		echo "D,#R,#X,#Y,B4.mu,B4.lo,B4.sd,2B.mu,      DEHB-6,DEHB-6_time,DEHB-12,DEHB-12_time,DEHB-18,DEHB-18_time,DEHB-24,DEHB-24_time,DEHB-50,DEHB-50_time,DEHB-100,DEHB-100_time,DEHB-200,DEHB-200_time,LITE-6,LITE-6_time,LITE-12,LITE-12_time,LITE-18,LITE-18_time,LITE-24,LITE-24_time,LITE-50,LITE-50_time,LITE-100,LITE-100_time,LITE-200,LITE-200_time,XPLOIT,XPLOIT_time,XPLORE,XPLORE_time,ADAPT,ADAPT_time,SWAY,SWAY_time,  LINE-6 ,  6 _time,  RANDOM-6,  6r_time, LINE-12, 12_time, RANDOM-12, 12r_time, LINE-18, 18_time, RANDOM-18, 18r_time, LINE-24 , 24 _time, RANDOM-24, 24r_time, LINE-50 , 50 _time, RANDOM-50, 50r_time,LINE-100 ,100 _time,RANDOM-100,100r_time,LINE-200 ,200 _time,RANDOM-200,200r_time,Before,File" > ../../results/optimization_performance/report_tmp.csv
		egrep csv comparez.out >>../../results/optimization_performance/report_tmp.csv
		awk 'BEGIN{FS=OFS=","} \
		NR==1 { \
			for (i=1; i<=NF; i++) { \
				if ($$i !~ /_time$$/ && $$i != "XPLOIT" && $$i != "XPLORE" && $$i != "ADAPT" && $$i != "SWAY") keep[i]=1 \
			} \
		} \
		{ \
			first = 1; \
			for (i=1; i<=NF; i++) if (keep[i]) { \
				if (!first) printf OFS; \
				printf "%s", $$i; \
				first=0 \
			} \
			print "" \
		}' ../../results/optimization_performance/report_tmp.csv > ../../results/optimization_performance/report.csv; \
		awk 'BEGIN{FS=OFS=","} \
		NR==1 { total_fields = NF } \
		NR>1 { \
			for (i=9; i<total_fields; i++) { \
				total[i]++; \
				if ($$i ~ /a$$/) count[i]++; \
			} \
		} \
		END { \
			printf ",,,,,,,,"; \
			for (i=9; i<total_fields; i++) { \
				pct = (count[i] ? int((100.0 * count[i] / total[i]) + 0.5) : 0); \
				printf "%s%d", (i>9 ? OFS : ""), pct; \
			} \
			printf ",\n" \
		}' ../../results/optimization_performance/report.csv >> ../../results/optimization_performance/report.csv


kill:
		ps | grep lua | grep -v vi | gawk '{system("kill -9 " $$1)}'  
