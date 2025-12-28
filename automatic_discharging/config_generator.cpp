#include <bits/stdc++.h>

using namespace std;
typedef pair<int, int> pii;

vector<int> alpha = {3,4,5,6,7,8,9,10,11};
string BASE_DIR = "./pending/";

void save_configurations(int n, const vector<vector<int> >& configs) {
    string path = BASE_DIR + to_string(n) + "-vertex.txt";
    ofstream out(path);
    if (!out) {
        cerr << "Failed to open file: " << path << endl;
        return;
    }

    for (const auto& config : configs) {
        assert(config.size() == n);
        for (int v : config) {
            out << v << " ";
        }
        out << "\n";
    }

    out.close();
}

int n_odd(const vector<vector<int> >& edges) {
    int cnt = 0;
    for(int v: alpha){
        if(edges[v].size() % 2 == 1) cnt++;
    }
    return cnt;
}

bool is_Eulerian(const vector<vector<int>>& edges, vector<int>& tour) {
    int N = edges.size();
    vector<multiset<int>> adj(N);

    int start = -1;
    for(auto u: alpha) {
        for (int v : edges[u]) {
            adj[u].insert(v);
            start = v;
        }
    }

    for(auto& lis: adj) {
        if(lis.size()%2 > 0) return false;
    }

    stack<int> st; st.push(start);

    // Hierholzer
    while (!st.empty()) {
        int v = st.top();

        if (!adj[v].empty()) {
            int u = *adj[v].begin();
            adj[v].erase(adj[v].begin());
            adj[u].erase(adj[u].find(v));
            st.push(u);
        } else {
            tour.push_back(v);
            st.pop();
        }
    }

    for(auto u: alpha) {
        if (!adj[u].empty()) return false;
    }

    return true;
}

void config_generator(const vector<pii>& v, int n) {
    vector<vector<int> > ret, edges(12);

    function<void(int, int, int)> combination = [&](int n, int dep, int prev) {
        if(2*(n-dep) < n_odd(edges)) return;
        if(dep == n){
            vector<int> tour;
            if(is_Eulerian(edges, tour)) {
                tour.pop_back();
                ret.push_back(tour);
            }
            return;
        }

        for(int i = prev; i < v.size(); ++i){
            edges[v[i].first].push_back(v[i].second);
            edges[v[i].second].push_back(v[i].first);
            combination(n, dep + 1, i);
            edges[v[i].first].pop_back();
            edges[v[i].second].pop_back();
        }
    };

    combination(n, 0, 0);

    save_configurations(n, ret);
}

int main() {    
    int light_ub = 11;
    for(int n = 3; n <= 10; n++) {
        vector<pii> v;
        for(int i = 0; i < alpha.size(); i++) {
            if(alpha[i]+n <= light_ub) continue;
            for(int j = i; j < alpha.size(); j++) {
                if(alpha[j]+n <= light_ub) continue;
                if(alpha[i] + alpha[j] <= light_ub) continue;
                v.push_back({alpha[i], alpha[j]});
            }
        }

        config_generator(v, n);
    }

    return 0;
}