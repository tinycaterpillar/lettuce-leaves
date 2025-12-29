#include <bits/stdc++.h>

using namespace std;
typedef pair<int, int> pii;

int LIGHT_UP = 11;
vector<int> vertices = {3,4,5,6,7,8,9,10,11}, alpha;
string BASE_DIR = "./pending/";

void save_configurations(int n, const set<vector<int> >& configs) {
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

vector<int> canonical_form(const vector<int>& config)
{
    int n = config.size();
    vector<int> best = config;

    // Original direction: check all rotations
    vector<int> tmp = config;
    for (int i = 0; i < n; i++) {
        if (tmp < best) best = tmp;
        rotate(tmp.begin(), tmp.begin() + 1, tmp.end());
    }

    // Reversed direction: check all rotations
    tmp.assign(config.rbegin(), config.rend());
    for (int i = 0; i < n; i++) {
        if (tmp < best) best = tmp;
        rotate(tmp.begin(), tmp.begin() + 1, tmp.end());
    }

    return best;
}

void config_generator(int n) {
    set<vector<int> > ret;
    vector<int> config;

    function<void(int, int)> combination = [&](int n, int dep) {
        if(dep == n){
            if(config.front()+config.back() > LIGHT_UP) ret.insert(canonical_form(config));;
            return;
        }

        for(auto v: alpha){
            if(!config.empty() && config.back()+v <= LIGHT_UP) continue;
            config.push_back(v);
            combination(n, dep+1);
            config.pop_back();
        }
    };

    combination(n, 0);

    save_configurations(n, ret);
}

int main() {    
    for(int n = 3; n <= 10; n++) {
        alpha.clear();
        for(auto v: vertices){
            if(n+v <= LIGHT_UP) continue;
            alpha.push_back(v);
        }

        config_generator(n);
    }

    return 0;
}