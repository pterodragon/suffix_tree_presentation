string = input()

pre_text = r'''
\begin{frame}[fragile,plain] \frametitle{Suffix Tree}
    \begin{figure}
        \begin{tikzpicture}[remember picture,overlay,level distance=50pt,->,line width=1.5pt]
            \tikzstyle{every node}=[draw,circle,inner sep=1pt,minimum size=7.5pt,line width=0.5pt]
            \tikzstyle{sll}=[bend left,dashed,line width=0.5pt,-{>[length=10pt]}]
            \tikzstyle{slr}=[bend right,dashed,line width=0.5pt,->]
            \tikzstyle{level 1}=[sibling distance=100pt]
            \tikzstyle{level 2}=[level distance=50pt,sibling distance=120pt]
            \tikzstyle{level 3}=[sibling distance=50pt]
'''  # NOQA
post_text = r'''
\node[rectangle,draw=none,yshift=10pt] at (current page.south) {
                    \parbox{.5\textwidth}{
                    \begin{figure}
                        \caption{Suffix Tree for ``$''' + string + r'''$''}
                    \end{figure}
                    }
            };
        \end{tikzpicture}
    \end{figure}
\end{frame}
'''  # NOQA

i = 0
while True:
    with open(f'st_{string}_out{i}.tex') as f:
        s = f.read()
    with open(f'st_{string}_out{i}.tex', 'w') as f:
        f.write(pre_text)
        f.write(s)
        f.write(post_text)
    i += 1
